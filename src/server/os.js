import {xu, fg} from "xu";
import {runUtil, fileUtil, sysUtil, printUtil, webUtil, cmdUtil} from "xutil";
import {path, delay} from "std";
import {OS_SERVER_HOST, OS_SERVER_PORT, OSIDS} from "../osUtil.js";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver-os",
	version : "1.0.0",
	desc    : "Handles sending scripts and files into various emulated operating systems and retrieving the results",
	opts    :
	{
		startedFilePath : {desc : "Path to write a file to when the server has started", hasValue : true, required : true},
		stopFilePath    : {desc : "Path to watch for a file to be created to stop the server", hasValue : true, required : true},
		logLevel        : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);

const OS_INSTANCE_DIR_PATH = "/mnt/dexvert/os";
const OS_INSTANCE_START_INTERVAL = 500;

const OS = {
	win2k :
	{
		debug       : false,
		qty         : 12,
		ramGB       : 2,
		scriptExt   : ".au3",
		emu         : "86Box",
		emuArgs     : () => (["86box.cfg"]),
		copy        : ["86box.cfg", "nvr"],
		hd          : ["hd.vhd"],
		archiveType : "zip"
	},
	winxp :
	{
		debug       : false,
		qty         : 14,
		ramGB       : 2,
		scriptExt   : ".au3",
		emu         : "86Box",
		emuArgs     : () => (["86box.cfg"]),
		copy        : ["86box.cfg", "nvr"],
		hd          : ["hd.vhd"],
		archiveType : "zip"
	},
	win7 :
	{
		debug     : false,
		qty       : 4,
		ramGB     : 16,
		cores     : 4,
		scriptExt : ".au3",
		emu       : "qemu-system-x86_64",
		emuArgs   : instance => ([
			"-nodefaults", "-machine", "accel=kvm,dump-guest-core=off", "-rtc", "base=2023-03-01T10:00:00", "-device", "virtio-rng-pci", "-m", "size=16G", "-smp", "cores=4", "-vga", "cirrus",
			//"-audiodev", "none,id=audio0", "-device", "ac97,audiodev=audio0",	// Used to enable sound if you discover any programs that need it
			"-drive", "format=qcow2,if=ide,index=0,file=hd.qcow2", "-boot", "order=c",
			"-netdev", `user,net=192.168.51.0/24,dhcpstart=192.168.51.${20+instance.instanceid},id=nd1`, "-device", "rtl8139,netdev=nd1", "-drive", `if=floppy,media=disk,file=${path.join(instance.dirPath, "instance.img")}`
		]),
		hd          : ["hd.qcow2"],
		archiveType : "zip"
	}
};

const RAM_PERCENTAGE_TARGET = 0.8;
const RAM_PERCENTAGE_TARGET_HOST = {eaglehollow : 0.4, crystalsummit : 0.4};

// reduce instance quantity to fit in 40% of available cores or 1 each if set to debug
const maxAvailableCores = Math.floor(navigator.hardwareConcurrency*0.40);
const totalDesiredCores = Object.values(OS).map(({qty}) => qty).sum();
for(const o of Object.values(OS))
	o.qty = o.debug ? 1 : Math.min(o.qty, Math.max(Math.floor(o.qty.scale(0, totalDesiredCores, 0, maxAvailableCores)), 2));	// eslint-disable-line sembiance/prefer-math-clamp

// reduce instance quantity to fit in X% of available RAM
const totalSystemRAM = (await sysUtil.memInfo()).total;
while((Object.values(OS).map(({qty, ramGB}) => qty*ramGB).sum()*xu.GB)>(totalSystemRAM*(RAM_PERCENTAGE_TARGET_HOST[Deno.hostname()] || RAM_PERCENTAGE_TARGET)))
	Object.values(OS).forEach(o => { o.qty = Math.max(1, o.qty-1); });

const HTTP_DIR_PATH = "/mnt/ram/dexvert/http";
const HTTP_IN_DIR_PATH = path.join(HTTP_DIR_PATH, "in");
const HTTP_OUT_DIR_PATH = path.join(HTTP_DIR_PATH, "out");

const INSTANCES = {};
const RUN_QUEUE = new Set();
const OS_DIR_PATH = path.join(import.meta.dirname, "..", "..", "os");
const CHECK_QUEUE_INTERVAL = 50;
const CMD_DURATIONS = {};

function prelog(instance)
{
	return `${fg.peach(instance.osid)}${fg.cyan("-")}${fg.yellow(instance.instanceid)} ${xu.paren(`VNC ${instance.vncPort}`)}${fg.cyan(":")}`;
}

let stopping = false;

const stopOS = async instance =>
{
	xlog.debug`${prelog(instance)} stopping...`;

	xlog.debug`${prelog(instance)} killing OS emu child process...`;
	if(instance.p)
		await runUtil.kill(instance.p, "SIGKILL").catch(() => {});

	xlog.debug`${prelog(instance)} deleting instance files...`;
	await runUtil.run("fixPerms", [], {cwd : instance.dirPath});
	await fileUtil.unlink(instance.dirPath, {recursive : true});
};

// Called to prepare the OS environment for a given OS and then start 86Box
const startOS = async (osid, instanceid) =>
{
	INSTANCES[osid] ||= {};
	
	const instance = {osid, instanceid, ready : false, busy : false};
	instance.dirPath = path.join(OS_INSTANCE_DIR_PATH, `${osid}-${instanceid}`);
	instance.debug = OS[osid].debug;
	instance.vncPort = 7900+(100*OSIDS.indexOf(osid))+instanceid;
	instance.scriptName = `go${OS[osid].scriptExt}`;
	INSTANCES[osid][instanceid] = instance;

	await Deno.mkdir(instance.dirPath, {recursive : true});
	
	for(const v of OS[osid].copy || [])
		await runUtil.run("rsync", runUtil.rsyncArgs(path.join(OS_DIR_PATH, osid, v), path.join(instance.dirPath, "/")));

	for(const v of OS[osid].hd)
	{
		if(v.endsWith(".vhd"))
			await runUtil.run("VBoxManage", ["createmedium", "disk", "--filename", path.join(instance.dirPath, v), "--format", "VHD", "--diffparent", path.join(OS_INSTANCE_DIR_PATH, osid, v)]);
		else if(v.endsWith(".qcow2"))
			await runUtil.run("qemu-img", ["create", "-F", "qcow2", "-b", path.join(OS_INSTANCE_DIR_PATH, osid, v), "-f", "qcow2", path.join(instance.dirPath, v)]);
	}

	await fileUtil.writeTextFile(path.join(instance.dirPath, "instance.txt"), instanceid.toString());
	await runUtil.run("/mnt/compendium/bin/mkFloppyFromFiles", [path.join(instance.dirPath, "instance.img"), path.join(instance.dirPath, "instance.txt")]);

	const emuOpts = {detached : true, cwd : instance.dirPath, env : {}};
	if(instance.debug)
	{
		emuOpts.env.DISPLAY = ":0";
		if(OS[osid].emu==="86Box")
			emuOpts.env.EMU86BOX_MOUSE = "evdev";
	}
	else
	{
		emuOpts.virtualX = true;
		emuOpts.virtualXVNCPort = instance.vncPort;
	}

	if(xlog.atLeast("debug"))
		emuOpts.liveOutput = true;

	xlog.debug`${prelog(instance)} Launching ${OS[osid].emu} with options ${printUtil.inspect(emuOpts).squeeze()}`;

	const instanceJSON = JSON.stringify(instance);
	const {p, cb} = await runUtil.run(OS[osid].emu, OS[osid].emuArgs ? OS[osid].emuArgs(instance) : [], emuOpts);
	instance.p = p;
	cb().then(async r =>
	{
		if(instance.debug)
			return;

		xlog[stopping ? "debug" : "error"]`${prelog(instance)} has exited with status ${r.status}${stopping ? "" : JSON.stringify(r)}`;
		if(!stopping)
		{
			if(instance.runTask && !instance.timedOut)
			{
				xlog[stopping ? "debug" : "error"]`${prelog(instance)} has outstanding runTask, re-adding to queue ${JSON.stringify(instance.runTask).squeeze()}`;
				instance.runTask.osPriority = true;
				RUN_QUEUE.add(instance.runTask);
				delete instance.runTask;
			}
			await stopOS(instance);
		}
		instance.timedOut = false;
		instance.ready = false;
		instance.p = null;
		delete INSTANCES[osid][instanceid];
		if(!stopping)
			await startOS(osid, instanceid);
	});

	xlog.info`${prelog(instance)} Launched. Waiting for it to boot...`;
	await fileUtil.writeTextFile(path.join(instance.dirPath, "instance.json"), instanceJSON);
};

const performRun = async (instance, runArgs) =>
{
	const startProcess = instance.p;
	const {body, reply, timeout} = runArgs;
	xlog.debug`${prelog(instance)} run with cmd ${body.cmd} and file ${(body.inFilePaths || [])[0]}`;
	xlog.debug`${prelog(instance)} run with request: ${body} and script ${body.script}`;

	let runErr = null;
	const runStartAt = performance.now();
	try
	{
		const inArchiveFilePath = path.join(HTTP_IN_DIR_PATH, instance.osid, `${instance.instanceid}.${OS[instance.osid].archiveType}`);
		const outarchiveFilePath = path.join(HTTP_OUT_DIR_PATH, instance.osid, `${instance.instanceid}.${OS[instance.osid].archiveType}`);

		// Copy our target files to a tmp dir. We use rsync here to handle both files and directories, it handles preserving timestamps, etc
		const tmpInDirPath = await fileUtil.genTempPath(undefined, "oshttp");
		await Deno.mkdir(tmpInDirPath, {recursive : true});
		await (body.inFilePaths || []).parallelMap(async inFilePath => await runUtil.run("rsync", ["-saL", inFilePath, path.join(tmpInDirPath, "/")]));

		const tmpGoFilePath = path.join(tmpInDirPath, instance.scriptName);
		await fileUtil.writeTextFile(tmpGoFilePath, body.script);

		// We create to a temp archive, and then copy it over in one go to prevent the supervisor from picking up an incomplete file
		const tmpInArchiveFilePath = await fileUtil.genTempPath(undefined, `.${OS[instance.osid].archiveType}`);
		if(OS[instance.osid].archiveType==="zip")
			await runUtil.run("zip", ["-r", tmpInArchiveFilePath, "."], {cwd : tmpInDirPath});
		else if(OS[instance.osid].archiveType==="lha")
			await runUtil.run("lha", ["c", tmpInArchiveFilePath, instance.scriptName, ...(body.inFilePaths || []).map(v => path.basename(v))], {cwd : tmpInDirPath});
		await fileUtil.unlink(tmpInDirPath, {recursive : true});
		await fileUtil.move(tmpInArchiveFilePath, inArchiveFilePath);

		// Wait for the OS to finish, which happens when the VM deletes the archive file via http calling /osDONE (or our instance process changes usually due to crashing)
		const finishedOK = await xu.waitUntil(async () => (!(await fileUtil.exists(inArchiveFilePath))) || instance.p!==startProcess, {timeout : (timeout ? timeout*1.5 : (xu.HOUR*2.2))});

		if(await fileUtil.exists(outarchiveFilePath))	// only exists if the OS was successful and called /osPOST with the result
		{
			if(OS[instance.osid].archiveType==="zip")
				await runUtil.run("unzip", ["-od", body.outDirPath, outarchiveFilePath]);
			else if(OS[instance.osid].archiveType==="lha")
				await runUtil.run("lha", ["-x", `-w=${body.outDirPath}`, outarchiveFilePath]);

			await fileUtil.unlink(outarchiveFilePath, {recursive : true});
		}
		else if(!finishedOK)
		{
			xlog.error`${prelog(instance)} timed out after ${timeout?.msAsHumanReadable({short : true})} waiting for runArgs to finish with files ${(body.inFilePaths || [])[0]} and runArgs: ${JSON.stringify(runArgs).squeeze()}`;
			instance.timedOut = true;	// this will prevent this file from being re-queued, assuming that if it timed out once it'll just do so again
			await runUtil.kill(instance.p, "SIGKILL").catch(() => {});
			await xu.waitUntil(() => instance.p!==startProcess);
		}
	}
	catch(err)
	{
		runErr = err;
	}

	delete instance.runTask;
	if(instance.p!==startProcess)
	{
		xlog.error`${prelog(instance)} process changed during run (crash? timeout w/kill?), so aborting run with runArgs ${JSON.stringify(runArgs).squeeze()}`;
		reply(new Response("ERROR os process changed during run due to crash or timeout, run aborted"));
		return;
	}
	
	const runDuration = performance.now()-runStartAt;
	CMD_DURATIONS[body.cmd] ||= [];
	CMD_DURATIONS[body.cmd].push({duration : runDuration, meta : body.meta || path.basename(body.inFilePaths[0])});
	xlog.debug`${prelog(instance)} finished request in ${runDuration}ms (${RUN_QUEUE.size} queued)`;
	instance.busy = false;

	if(runErr)
		xlog.error`${prelog(instance)} ERROR ${runErr} with runArgs ${JSON.stringify(runArgs).squeeze()}`;

	reply(new Response(runErr ? runErr.toString() : "ok"));
};

const checkRunQueue = () =>
{
	if(RUN_QUEUE.size===0)
		return setTimeout(() => checkRunQueue(), CHECK_QUEUE_INTERVAL);

	const seenOSIDs = new Set();
	const runPair = {};

	// some items have a higher priority than others, but being a Set we can't change the order, so we make a temporary array that has the high priority items first. we also use [].concat instead of rest params to avoid call stack overflow
	const prioritizedQueueArray = [].concat(Array.from(RUN_QUEUE).filter(v => v.osPriority), Array.from(RUN_QUEUE).filter(v => !v.osPriority));
	for(const runTask of prioritizedQueueArray)
	{
		if(seenOSIDs.has(runTask.body.osid))
			continue;
		
		seenOSIDs.add(runTask.body.osid);
		const instance = Object.values(INSTANCES[runTask.body.osid] || {}).find(o => o.ready && !o.busy);
		if(instance)
		{
			runPair.instance = instance;
			runPair.runTask = runTask;
			break;
		}
	}

	if(runPair.instance && runPair.runTask)
	{
		runPair.instance.busy = true;
		RUN_QUEUE.delete(runPair.runTask);
		runPair.instance.runTask = runPair.runTask;
		performRun(runPair.instance, runPair.runTask);
	}

	setTimeout(() => checkRunQueue(), 0);
};

const cleanup = async () =>
{
	xlog.info`Cleaning up previous instances...`;

	//xlog.debug`Stopping all existing OS emu procs...`;
	//await runUtil.run("sudo", ["killall", "--wait", "-9", ...Object.values(OS).map(({emu}) => emu).unique()]);

	xlog.debug`Deleting previous instance files...`;
	await runUtil.run("fixPerms", [], {cwd : OS_INSTANCE_DIR_PATH});
	await fileUtil.unlink(OS_INSTANCE_DIR_PATH, {recursive : true});

	xlog.debug`Deleting previous HTTP in/out files...`;
	await fileUtil.unlink(HTTP_DIR_PATH, {recursive : true});
};

await cleanup();

const routes = new Map();
routes.set("/status", async () =>	// eslint-disable-line require-await
{
	const r = {queueSize : RUN_QUEUE.size, activeSize : Object.values(INSTANCES).flatMap(o => Object.values(o)).filter(v => v.ready && v.busy).length};
	if(RUN_QUEUE.size)
		r.queue = Array.from(RUN_QUEUE, v => { const o = Object.fromEntries(Object.entries(v.body)); delete o.script; return o; });
		
	r.instancesAvailable = Object.fromEntries(Object.entries(INSTANCES).map(([osid, instances]) => ([osid, Object.values(instances).filter(v => v.ready && !v.busy).length])));
	r.instances = INSTANCES;
	r.cmdDurations = Object.entries(CMD_DURATIONS).map(([cmd, metaDurations]) =>
	{
		const durations = metaDurations.map(md => md.duration);
		const o = {cmd, count : durations.length, avg : durations.average(), median : durations.median(), stdDev : durations.standardDeviation(), variance : durations.variance(), max : durations.max()};
		o.metas = metaDurations.map(md => md.meta).unique().map(meta => ({meta, count : metaDurations.filter(md => md.meta===meta).length}));
		return o;
	}).sortMulti([o => o.count, o => o.cmd], [true, false]);
	return Response.json(r);
});

routes.set("/osRun", async request =>
{
	const body = await request.json();
	xlog.trace`Got osRun request for ${body.osid} adding to queue (${RUN_QUEUE.size+1} queued)`;
	let response = null;
	RUN_QUEUE.add({body, request, reply : v => { response = v; }});
	await xu.waitUntil(() => !!response);
	return response;
});

routes.set("/osReady", async request =>	// eslint-disable-line require-await
{
	const body = Object.fromEntries(["osid", "instanceid"].map(k => ([k, new URL(request.url).searchParams.get(k)])));
	const instance = Object.values(INSTANCES[body.osid]).find(v => v.instanceid===+body.instanceid);
	xlog.info`${prelog(instance)} Called /osReady`;
	instance.ready = true;
	return new Response("ok");
});

routes.set("/osGET", async request =>
{
	const body = Object.fromEntries(["osid", "instanceid"].map(k => ([k, new URL(request.url).searchParams.get(k)])));
	xlog.trace`Got osGET from ${body.osid}-${body.instanceid}`;
	const inArchiveFilePath = path.join(HTTP_IN_DIR_PATH, body.osid, `${body.instanceid}.${OS[body.osid].archiveType}`);
	if(!(await fileUtil.exists(inArchiveFilePath)))
		return new Response(null, {status : 404});
				
	const inArchive = await Deno.open(inArchiveFilePath, {read : true});
	return new Response(inArchive.readable, {headers : {"Content-Type" : "application/octet-stream"}});
});

routes.set("/osPOST", async request =>
{
	const body = Object.fromEntries(["osid", "instanceid"].map(k => ([k, new URL(request.url).searchParams.get(k)])));
	const requestArrayBuffer = await request.arrayBuffer();
	xlog.debug`Got osPOST from ${body.osid}-${body.instanceid} with a buffer ${requestArrayBuffer.byteLength} bytes long`;
	await Deno.writeFile(path.join(HTTP_OUT_DIR_PATH, body.osid, `${body.instanceid}.${OS[body.osid].archiveType}`), new Uint8Array(requestArrayBuffer));
	return new Response("", {status : 200});
});

routes.set("/osDONE", async request =>
{
	const body = Object.fromEntries(["osid", "instanceid"].map(k => ([k, new URL(request.url).searchParams.get(k)])));
	xlog.debug`Got osDONE from ${body.osid}-${body.instanceid}`;
	await fileUtil.unlink(path.join(HTTP_IN_DIR_PATH, body.osid, `${body.instanceid}.${OS[body.osid].archiveType}`), {recursive : true});
	return new Response("", {status : 200});
});

const webServer = webUtil.serve({hostname : OS_SERVER_HOST, port : OS_SERVER_PORT}, await webUtil.route(routes), {xlog});

await Deno.mkdir(path.join(OS_INSTANCE_DIR_PATH), {recursive : true});

const instanceids = [];
for(const osid of Object.keys(OS))
{
	xlog.info`Preparing HDs for ${osid}...`;

	await Deno.mkdir(path.join(HTTP_IN_DIR_PATH, osid), {recursive : true});
	await Deno.mkdir(path.join(HTTP_OUT_DIR_PATH, osid), {recursive : true});

	instanceids.push(...[].pushSequence(0, OS[osid].qty-1).map(v => ([osid, v])));

	// we need to copy the parent/backing HD to the instance dir, because even though it's just a backing HD VBoxManage still modifies the thing and we don't want to touch the original at all otherwise we have to re-copy it to dexdrones every time
	const osInstanceDirPath = path.join(OS_INSTANCE_DIR_PATH, osid);
	await Deno.mkdir(osInstanceDirPath, {recursive : true});
	for(const v of OS[osid].hd)
		await runUtil.run("rsync", runUtil.rsyncArgs(path.join(OS_DIR_PATH, osid, v), path.join(osInstanceDirPath, v), {fast : true}), {liveOutput : true});
}

// startOS above calls VBoxManage createmedium which then 'registers' both the parent and child HDs in some VBoxManage config. This can cause issues during development if HD paths change, So we clear out all previous HDs here just to be safe
xlog.info`Clearing previous VBoxManaged hdds...`;
const {stdout : vboxDiskLines} = await runUtil.run("VBoxManage", ["list", "hdds"]);
const vboxDiskPaths = [];
for(const vboxDiskLine of vboxDiskLines.trim().split("\n"))
{
	if(vboxDiskLine.startsWith("Location:"))
		vboxDiskPaths.push(vboxDiskLine.substring("Location:".length+1).trim());
}

for(const vboxDiskPath of vboxDiskPaths.sortMulti([v => Object.keys(OS).some(osid => v.startsWith(path.join(OS_INSTANCE_DIR_PATH, `${osid}-`)))], [true]))
	await runUtil.run("VBoxManage", ["closemedium", "disk", vboxDiskPath]);

xlog.info`Starting instances...`;
await Promise.all(await instanceids.parallelMap(async ([osid, instanceid], i) =>
{
	await delay(OS_INSTANCE_START_INTERVAL*i);
	await startOS(osid, instanceid);
	return xu.waitUntil(() => INSTANCES[osid][instanceid]?.ready);	// note we don't await here
}, instanceids.length));

checkRunQueue();

// wait for all instances to be fully readu
const instancesFlat = Object.values(INSTANCES).flatMap(o => Object.values(o));
await xu.waitUntil(() => (Object.keys(OS).length===0 || (instancesFlat.length>0 && instancesFlat.every(instance => instance.p && instance.ready))));
await fileUtil.writeTextFile(argv.startedFilePath, "");

// wait until we are told to stop
await xu.waitUntil(async () => await fileUtil.exists(argv.stopFilePath));
xlog.info`Stopping...`;
stopping = true;
webServer.stop();

for(const instance of Object.values(INSTANCES).flatMap(o => Object.values(o)))
	await stopOS(instance);

await cleanup();

await fileUtil.unlink(argv.stopFilePath);
