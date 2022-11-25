import {xu, fg} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {path, delay, streams} from "std";
import {WebServer} from "WebServer";
import {QEMU_SERVER_HOST, QEMU_SERVER_PORT} from "../qemuUtil.js";

const QEMU_INSTANCE_DIR_PATH = "/mnt/dexvert/qemu";

const DEBUG = false;	// Set this to true on lostcrag to restrict each VM to just 1 instance and visually show it on screen
const BASE_SUBNET = 50;
const DELAY_SIZE = xu.MB*50;
const DELAY_AMOUNT = xu.SECOND/2;

// We specify a given dateTime in order to prevent certain old shareware programs from expiring (Awave Studio)
const OS_DEFAULT =
{
	dateTime     : "2021-04-18T10:00:00",
	smbGuestPort : 445,
	sshGuestPort : 22,
	machine      : "accel=kvm",
	hdOpts       : ",if=ide"
};

const qty = maxQty => (DEBUG ? 1 : (Math.min(maxQty, (Deno.hostname().startsWith("slim") ? maxQty*0.5 : ({lostcrag : 4, crystalsummit : 2}[Deno.hostname()] || maxQty)))));
const OS =
{
	win2k    : { qty : qty(14), ram : "1G", arch :   "i386", inOutType : "mount", scriptExt :  ".au3", cores : 1, extraArgs : ["-nodefaults", "-vga", "cirrus"], extraImgs : ["pagefile.img"] },
	winxp    : { qty : qty(14), ram : "3G", arch :   "i386", inOutType : "mount", scriptExt :  ".au3", cores : 8, extraArgs : ["-nodefaults", "-vga", "cirrus"] },	// don't reduce cores, will break programs that took a hardware id snapshot on install
	amigappc : { qty :  qty(6), ram : "1G", arch :    "ppc", inOutType :  "http", scriptExt : ".rexx", cores : 1, machine : "type=sam460ex", net : "ne2k_pci", hdOpts : ",id=disk", extraArgs : ["-device", "ide-hd,drive=disk,bus=ide.0"]},
	gentoo   : { qty :  qty(8), ram : "2G", arch : "x86_64", inOutType :   "ssh", scriptExt :   ".sh", cores : 4, hdOpts : ",if=virtio", net : "virtio-net", extraArgs : ["-device", "virtio-rng-pci", "-vga", "std"] }
};
const SUBNET_ORDER = ["win2k", "winxp", "amigappc", "gentoo"];
Object.keys(OS).sortMulti([v => SUBNET_ORDER.indexOf(v)]).forEach(v => { OS[v].subnet = BASE_SUBNET + SUBNET_ORDER.indexOf(v); });

const HTTP_DIR_PATH = "/mnt/ram/dexvert/http";
const HTTP_IN_DIR_PATH = path.join(HTTP_DIR_PATH, "in");
const HTTP_OUT_DIR_PATH = path.join(HTTP_DIR_PATH, "out");

const INSTANCES = {};
const RUN_QUEUE = new Set();
const QEMU_DIR_PATH = path.join(xu.dirname(import.meta), "..", "..", "qemu");
const CHECK_QUEUE_INTERVAL = 50;
const CHECK_QUEUE_TOO_LONG = xu.MINUTE*5;

function prelog(instance)
{
	return `${instance.osid} #${instance.instanceid} (VNC ${instance.vncPort}):`;
}

export class qemu extends Server
{
	checkQueueCounter = 0;
	serversLaunched = false;
	IN_OUT_LOGIC = {
		mount : async (instance, {body}) =>
		{
			const inDirPath = path.join(instance.dirPath, "in");
			const outDirPath = path.join(instance.dirPath, "out");
			const goFilePath = path.join(inDirPath, instance.scriptName);
			const tmpGoFilePath = await fileUtil.genTempPath(undefined, path.extname(instance.scriptName));
			const totalFilesSize = (await body.inFilePaths.parallelMap(async inFilePath => (await Deno.stat(inFilePath)).size)).sum();

			this.xlog.debug`${prelog(instance)} rsyncing files ${body.inFilePaths} to ${inDirPath}`;

			// First make an attempt to clear the in and out dir of any previous stuck files
			await fileUtil.emptyDir(inDirPath);
			await fileUtil.emptyDir(outDirPath);

			// We use rsync here to handle both files and directories, it handles preserving timestamps, etc
			await (body.inFilePaths || []).parallelMap(async inFilePath => await runUtil.run("rsync", ["-saL", inFilePath, path.join(inDirPath, "/")]));

			// If the input file is >50MB then we should wait 1 second PER 50MB to allow the mount to fully catch up
			if(totalFilesSize>=DELAY_SIZE)
			{
				const timeToWait = Math.floor(totalFilesSize/DELAY_SIZE)*DELAY_AMOUNT;
				this.xlog.info`${prelog(instance)} is waiting ${timeToWait/xu.SECOND} seconds for the mount to fully see the INPUT files due to their large size ${totalFilesSize.bytesToSize()}`;
				await delay(timeToWait);
			}

			this.xlog.debug`${prelog(instance)} Writing go script to tmp file ${tmpGoFilePath}`;

			// We write the go script to a temp file first, and then copy it over in one go to prevent the supervisor from picking up an incomplete file
			await fileUtil.writeTextFile(tmpGoFilePath, body.script);
			await fileUtil.move(tmpGoFilePath, goFilePath, this);

			this.xlog.debug`${prelog(instance)} Awaiting VM to finish and delete the go script....`;

			// Wait for finish, which happens when the VM deletes the go file
			await xu.waitUntil(async () => (!(await fileUtil.exists(goFilePath))));

			// If the input file was >50MB then we should wait 1 second PER 50MB to allow the output files on the mount to fully catch up
			if(totalFilesSize>=DELAY_SIZE)
			{
				const timeToWait = Math.floor(totalFilesSize/DELAY_SIZE)*DELAY_AMOUNT;
				this.xlog.info`${prelog(instance)} waiting ${timeToWait/xu.SECOND} seconds for the mount to fully see the OUPUT files due to their large size ${totalFilesSize.bytesToSize()}`;
				await delay(timeToWait);
			}

			// We use rsync here to preserve timestamps
			await runUtil.run("rsync", ["-sa", path.join(outDirPath, "/"), path.join(body.outDirPath, "/")]);

			await fileUtil.emptyDir(inDirPath);
			await fileUtil.emptyDir(outDirPath);
		},
		http : async (instance, {body}) =>
		{
			const tmpInLHAFilePath = await fileUtil.genTempPath(undefined, ".lha");
			const tmpInDirPath = await fileUtil.genTempPath(undefined, "qemuhttp");
			const tmpGoFilePath = path.join(tmpInDirPath, instance.scriptName);
			const inLHAFilePath = path.join(HTTP_IN_DIR_PATH, `${instance.ip}.lha`);
			const outLHAFilePath = path.join(HTTP_OUT_DIR_PATH, `${instance.ip}.lha`);

			await Deno.mkdir(tmpInDirPath, {recursive : true});

			// We use rsync here to handle both files and directories, it handles preserving timestamps, etc
			await (body.inFilePaths || []).parallelMap(async inFilePath => await runUtil.run("rsync", ["-saL", inFilePath, path.join(tmpInDirPath, "/")]));

			await fileUtil.writeTextFile(tmpGoFilePath, body.script);

			// We create to a temp LHA first, and then copy it over in one go to prevent the supervisor from picking up an incomplete file
			await runUtil.run("lha", ["c", tmpInLHAFilePath, instance.scriptName, ...(body.inFilePaths || []).map(v => path.basename(v))], {cwd : tmpInDirPath});
			await fileUtil.move(tmpInLHAFilePath, inLHAFilePath, this);

			// Wait for finish, which happens when the VM deletes the lha file
			await xu.waitUntil(async () => (!(await fileUtil.exists(inLHAFilePath))));

			await runUtil.run("lha", ["-x", `-w=${body.outDirPath}`, outLHAFilePath]);

			await fileUtil.unlink(tmpInDirPath, {recursive : true});
			await fileUtil.unlink(outLHAFilePath, {recursive : true});
		},
		ssh : async (instance, {body}) =>
		{
			const sshOpts = ["-i", path.join(QEMU_DIR_PATH, instance.osid, "dexvert_id_rsa"), "-o", "StrictHostKeyChecking=no", "-p", instance.inOutHostPort];
			const sshPrefix = "dexvert@127.0.0.1";
			const inDirPath = "/in";
			const outDirPath = "/out";
			const goFilePath = path.join(inDirPath, instance.scriptName);
			const tmpGoFilePath = await fileUtil.genTempPath(undefined, path.extname(instance.scriptName));

			// We use rsync here to handle both files and directories, it handles preserving timestamps, etc
			await (body.inFilePaths || []).parallelMap(async inFilePath => await runUtil.run("rsync", ["-saL", "-e", `ssh ${sshOpts.join(" ")}`, inFilePath, path.join(`${sshPrefix}:${inDirPath}`, "/")]));

			await fileUtil.writeTextFile(tmpGoFilePath, body.script);
			await runUtil.run("scp", [...sshOpts.map(v => (v==="-p" ? "-P" : v)), tmpGoFilePath, `${sshPrefix}:${goFilePath}`]);
			
			// Wait for finish, which happens when we detect that the go file has disappeared
			await xu.waitUntil(async () =>
			{
				const {stdout} = await runUtil.run("ssh", [...sshOpts, sshPrefix, "ls", goFilePath]);
				return (stdout.trim()!==goFilePath);
			});

			// We use rsync here to preserve timestamps
			await runUtil.run("rsync", ["-saL", "-e", `ssh ${sshOpts.join(" ")}`, path.join(`${sshPrefix}:${outDirPath}`, "/"), path.join(body.outDirPath, "/")]);

			await fileUtil.unlink(tmpGoFilePath);
			await runUtil.run("ssh", [...sshOpts, sshPrefix, "rm", "-rf", path.join(inDirPath, "*")]);
			await runUtil.run("ssh", [...sshOpts, sshPrefix, "rm", "-rf", path.join(outDirPath, "*")]);
		}
	};
	
	baseKeys = Object.keys(this);

	// Called to prepare the QEMU environment for a given OS and then start QEMU
	async startOS(osid, instanceid, startingFromStop)
	{
		INSTANCES[osid] ||= {};
		
		const instance = {osid, instanceid, dirPath : path.join(QEMU_INSTANCE_DIR_PATH, `${osid}-${instanceid}`), ready : false, busy : false};
		instance.debug = DEBUG || OS[osid].debug;
		instance.ip = `192.168.${OS[osid].subnet}.${20+instanceid}`;
		instance.inOutHostPort = +`${OS[osid].subnet}${20+instanceid}`;
		instance.vncPort = (((OS[osid].subnet-BASE_SUBNET)+1)*100)+instanceid;
		instance.scriptName = `go${OS[osid].scriptExt}`;
		instance.inOutType = OS[osid].inOutType;
		INSTANCES[osid][instanceid] = instance;
		
		await Deno.mkdir(path.join(instance.dirPath, "in"), {recursive : true});
		await Deno.mkdir(path.join(instance.dirPath, "out"), {recursive : true});

		const imgFilePaths = ["hd.img", ...(OS[osid].extraImgs || [])].map(imgFilename => path.join(QEMU_INSTANCE_DIR_PATH, osid, imgFilename));
		await imgFilePaths.parallelMap(imgFilePath => Deno.copyFile(imgFilePath, path.join(instance.dirPath, path.basename(imgFilePath))));

		const qemuArgs = ["-drive", `format=raw,file=hd.img${OS[osid].hdOpts || OS_DEFAULT.hdOpts}`];
		if(!instance.debug)
			qemuArgs.push("-nographic", "-vnc", `127.0.0.1:${instance.vncPort},share=force-shared`);
		qemuArgs.push("-machine", `${OS[osid].machine || OS_DEFAULT.machine},dump-guest-core=off`);
		qemuArgs.push("-m", `size=${OS[osid].ram}`);
		qemuArgs.push("-rtc", `base=${OS[osid].dateTime || OS_DEFAULT.dateTime}`);
		if((OS[osid].cores || 1)>1)
			qemuArgs.push("-smp", `cores=${OS[osid].cores}`);
		
		let netDevVal = `user,net=192.168.${OS[osid].subnet}.0/24,dhcpstart=${instance.ip},id=nd1`;
		if(instance.inOutType==="mount")
			netDevVal += `,hostfwd=tcp:127.0.0.1:${instance.inOutHostPort}-${instance.ip}:${OS[osid].smbGuestPort || OS_DEFAULT.smbGuestPort}`;
		else if(instance.inOutType==="ssh")
			netDevVal += `,hostfwd=tcp:127.0.0.1:${instance.inOutHostPort}-${instance.ip}:${OS[osid].sshGuestPort || OS_DEFAULT.sshGuestPort}`;
		qemuArgs.push("-netdev", netDevVal);

		qemuArgs.push("-device", `${OS[osid].net || "rtl8139"},netdev=nd1`);

		(OS[osid].extraImgs || []).forEach(extraImg => qemuArgs.push("-drive", `format=raw,file=${extraImg}${OS[osid].hdOpts || OS_DEFAULT.hdOpts}`));

		qemuArgs.push(...OS[osid].extraArgs || []);

		const qemuRunOptions = {detached : true, cwd : instance.dirPath};
		if(instance.debug)
			qemuRunOptions.env = {DISPLAY : (Deno.hostname()==="crystalsummit" ? ":0.1" : ":0")};

		await delay(Math.randomInt(xu.SECOND, xu.SECOND*5));

		this.xlog.info`Launching ${osid} #${instanceid}: qemu-system-${OS[osid].arch} ${xu.inspect(qemuArgs).squeeze()} and options ${xu.inspect(qemuRunOptions).squeeze()}`;

		instance.qemuRunOptions = qemuRunOptions;
		instance.qemuArgs = qemuArgs;
		const instanceJSON = JSON.stringify(instance);
		const {p, cb} = await runUtil.run(`qemu-system-${OS[osid].arch}`, qemuArgs, qemuRunOptions);
		instance.p = p;
		cb().then(async r =>
		{
			this.xlog[this.stopping ? "info" : "error"]`${prelog(instance)} has exited with status ${r.status}${this.stopping ? "" : `${r}`}`;
			if(!this.stopping && !startingFromStop)
				await this.stopOS(instance);
			instance.ready = false;
			instance.p = null;
			delete INSTANCES[osid][instanceid];
			if(!this.stopping && !startingFromStop)
				await this.startOS(osid, instanceid, true);
		});

		this.xlog.info`${prelog(instance)} launched, waiting for it to boot...`;
		await fileUtil.writeTextFile(path.join(instance.dirPath, "instance.json"), instanceJSON);
	}

	// Called when the QEMU has fully booted and is ready to received files
	async readyOS(instance)
	{
		this.xlog.info`${prelog(instance)} declared itself ready!`;
		if(instance.inOutType==="mount")
		{
			this.xlog.info`${instance.osid} #${instance.instanceid} mounting in/out...`;
			const mountArgs = ["-t", "cifs", "-o", `user=dexvert,pass=dexvert,port=${instance.inOutHostPort},vers=1.0,sec=ntlm,gid=1000,uid=7777`];
			for(const v of ["in", "out"])
			{
				const mountDirPath = path.join(instance.dirPath, v);
				const {stdout : mountStdout, stderr : mountStderr} = await runUtil.run("sudo", ["mount", ...mountArgs, `//127.0.0.1/${v}`, mountDirPath], {verbose : this.xlog.atLeast("debug")});
				const {stdout : mountStatus} = await runUtil.run("sudo", ["findmnt", "--output", "FSTYPE", "--noheadings", mountDirPath]);
				if(mountStatus.trim().toLowerCase()!=="cifs")
					throw new Error(`Failed to mount ${v} with args ${mountArgs} to ${mountDirPath} with mount stdout ${mountStdout} and stderr ${mountStderr}`);
			}
		}

		this.xlog.info`${prelog(instance)} fully ready! (VNC ${5900 + instance.vncPort})`;
		instance.ready = true;
	}

	async performRun(instance, runArgs)
	{
		const {body, reply} = runArgs;
		this.xlog.info`${prelog(instance)} run with cmd ${body.cmd} and file ${(body.inFilePaths || [])[0]}`;
		this.xlog.debug`${prelog(instance)} run with request: ${body} and script ${body.script}`;

		let inOutErr = null;
		await this.IN_OUT_LOGIC[instance.inOutType](instance, runArgs).catch(err => { inOutErr = err; });
		this.xlog.info`${prelog(instance)} finished request (${RUN_QUEUE.size} queued)`;
		instance.busy = false;

		if(inOutErr)
			this.xlog.error`${prelog(instance)} ERROR ${inOutErr} with runArgs ${JSON.stringify(runArgs).squeeze()}`;

		reply(new Response(inOutErr ? inOutErr.toString() : "ok"));
	}

	checkRunQueue()
	{
		if(RUN_QUEUE.size===0)
		{
			this.checkQueueCounter = 0;
			return setTimeout(() => this.checkRunQueue(), CHECK_QUEUE_INTERVAL);
		}

		const seenOSIDs = new Set();
		const runPair = {};

		// some items have a higher priority than others, but being a Set we can't change the order, so we make a temporary array that has the high priority items first. we also use [].concat instead of rest params to avoid call stack overflow
		const prioritizedQueueArray = [].concat(Array.from(RUN_QUEUE).filter(v => v.qemuPriority), Array.from(RUN_QUEUE).filter(v => !v.qemuPriority));	// eslint-disable-line sembiance/disfavor-array-concat
		for(const runTask of prioritizedQueueArray)
		{
			if(seenOSIDs.has(runTask.body.osid))
				continue;
			
			seenOSIDs.add(runTask.body.osid);
			const instance = Object.values(INSTANCES[runTask.body.osid]).find(o => o.ready && !o.busy);
			if(instance)
			{
				runPair.instance = instance;
				runPair.runTask = runTask;
				break;
			}
		}

		if(runPair.instance && runPair.runTask)
		{
			this.checkQueueCounter = 0;
			runPair.instance.busy = true;
			RUN_QUEUE.delete(runPair.runTask);
			this.performRun(runPair.instance, runPair.runTask);
		}
		else
		{
			this.checkQueueCounter++;
			if(this.checkQueueCounter>((CHECK_QUEUE_TOO_LONG/CHECK_QUEUE_INTERVAL)))
			{
				this.xlog.warn`QEMU queue has been stuck for over 1 minute with ${RUN_QUEUE.size} items in queue. Instance status:`;
				for(const subInstance of Object.values(INSTANCES).flatMap(o => Object.values(o)))
					this.xlog.warn`${fg.peach("STATUS OF")} ${prelog(subInstance)}: ${{ready : subInstance.ready, busy : subInstance.busy}}`;

				this.checkQueueCounter = 0;
			}
		}

		setTimeout(() => this.checkRunQueue(), 0);
	}

	async start()
	{
		this.xlog.info`Unmounting previous mounts...`;
		await runUtil.run(path.join(QEMU_DIR_PATH, "unmountDeadMounts.sh"), []);

		this.xlog.info`Stopping all existing QEMU procs...`;
		await runUtil.run("sudo", ["killall", "--wait", "qemu-system-x86_64", "qemu-system-i386", "qemu-system-ppc"]);

		this.webServer = new WebServer(QEMU_SERVER_HOST, QEMU_SERVER_PORT, {xlog : this.xlog});
		
		this.webServer.add("/status", async () => new Response(JSON.stringify({queueSize : RUN_QUEUE.size})), {logCheck : () => false});	// eslint-disable-line require-await

		this.webServer.add("/qemuReady", async request =>
		{
			const u = new URL(request.url);
			const body = Object.fromEntries(["osid", "ip"].map(k => ([k, u.searchParams.get(k)])));
			this.xlog.info`Got qemuReady request from ${fg.peach(body.osid)}${fg.cyan("@")}${fg.yellow(body.ip)}`;
			await this.readyOS(Object.values(INSTANCES[body.osid]).find(v => v.ip===body.ip));
			return new Response("ok");
		});
		
		this.webServer.add("/qemuRun", async (request, reply) =>
		{
			const body = await request.json();
			this.xlog.info`Got qemuRun request for ${body.osid} adding to queue (${RUN_QUEUE.size+1} queued)`;
			RUN_QUEUE.add({body, request, reply});
		}, {detached : true, method : "POST", logCheck : () => false});
		
		await Deno.mkdir(HTTP_IN_DIR_PATH, {recursive : true});
		await Deno.mkdir(HTTP_OUT_DIR_PATH, {recursive : true});
		this.webServer.add("/qemuGET", async (request, reply) =>
		{
			const ipAddress = (new URL(request.url)).searchParams.get("ip");
			this.xlog.debug`Got qemuGET from IP ${ipAddress}`;
			const inLHAFilePath = path.join(HTTP_IN_DIR_PATH, `${ipAddress}.lha`);
			if(!(await fileUtil.exists(inLHAFilePath)))
				return reply(new Response(null, {status : 404}));
						
			const inLHA = await Deno.open(inLHAFilePath, {read : true});
			reply(new Response(streams.readableStreamFromReader(inLHA), {headers : {"Content-Type" : "application/octet-stream"}}));
		}, {detached : true, method : "GET", logCheck : () => false});

		this.webServer.add("/qemuPOST", async (request, reply) =>
		{
			const ipAddress = (new URL(request.url)).searchParams.get("ip");
			const requestArrayBuffer = await request.arrayBuffer();
			this.xlog.debug`Got qemuPOST from IP ${ipAddress} with a buffer ${requestArrayBuffer.byteLength} bytes long`;
			await Deno.writeFile(path.join(HTTP_OUT_DIR_PATH, `${ipAddress}.lha`), new Uint8Array(requestArrayBuffer));
			await fileUtil.unlink(path.join(HTTP_IN_DIR_PATH, `${ipAddress}.lha`), {recursive : true});
			reply(new Response("", {status : 200}));
		}, {detached : true, method : "POST", logCheck : () => false});

		this.webServer.add("/qemuDONE", async (request, reply) =>
		{
			const ipAddress = (new URL(request.url)).searchParams.get("ip");
			this.xlog.debug`Got qemuDONE from IP ${ipAddress}`;
			await fileUtil.unlink(path.join(HTTP_IN_DIR_PATH, `${ipAddress}.lha`), {recursive : true});
			reply(new Response("", {status : 200}));
		}, {detached : true, method : "GET"});

		await this.webServer.start();

		this.xlog.info`Finding old QEMU instances...`;
		const oldQEMUInstanceDirPaths = await fileUtil.tree(QEMU_INSTANCE_DIR_PATH, {depth : 1, nofile : true, regex : /-\d+$/});

		this.xlog.info`Deleting ${oldQEMUInstanceDirPaths.length} previous QEMU instances...`;
		for(const oldQEMUInstanceDirPath of oldQEMUInstanceDirPaths)
			await fileUtil.unlink(oldQEMUInstanceDirPath, {recursive : true});

		for(const osid of Object.keys(OS))
			await Deno.mkdir(path.join(QEMU_INSTANCE_DIR_PATH, osid), {recursive : true});

		this.xlog.info`Ensuring img files are up to date...`;
		for(const [osid, osInfo] of Object.entries(OS))
		{
			for(const imgFilePath of ["hd.img", ...(osInfo.extraImgs || [])].map(imgFilename => path.join(QEMU_DIR_PATH, osid, imgFilename)))
			{
				const imgDestFilePath = path.join(QEMU_INSTANCE_DIR_PATH, osid, path.basename(imgFilePath));
				this.xlog.info`Rsyncing to: ${imgDestFilePath}`;
				await runUtil.run("rsync", ["-sa", imgFilePath, imgDestFilePath]);
			}
		}

		this.xlog.info`Starting instances...`;
		await Object.keys(OS).parallelMap(async osid => await [].pushSequence(0, OS[osid].qty-1).parallelMap(instanceid => this.startOS(osid, instanceid)), Object.keys(OS).length);

		this.serversLaunched = true;
		this.checkRunQueue();
	}

	status()
	{
		const instances = Object.values(INSTANCES).flatMap(o => Object.values(o));
		return this.serversLaunched && instances.length>0 && instances.every(instance => instance.p && instance.ready);
	}

	async stopOS(instance)
	{
		this.xlog.info`${prelog(instance)} stopping...`;
		if(instance.inOutType==="mount")
		{
			this.xlog.info`${prelog(instance)} unmounting in/out...`;
			for(const v of ["in", "out"])
				await runUtil.run("sudo", ["umount", "-lf", path.join(instance.dirPath, v)], {timeout : xu.SECOND*20});
		}

		this.xlog.info`${prelog(instance)} killing qemu child process...`;
		if(instance.p)
			await runUtil.kill(instance.p, "SIGKILL").catch(() => {});
	}

	async stop()
	{
		this.stopping = true;
		
		if(this.webServer)
			this.webServer.stop();
		
		for(const instance of Object.values(INSTANCES).flatMap(o => Object.values(o)))
			await this.stopOS(instance);
	}
}
