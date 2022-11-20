import {xu, fg} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil, cmdUtil} from "xutil";
import {path, delay} from "std";

await runUtil.checkNumserver();

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver",
	version : "1.0.0",
	desc    : "Starts needed background services for dexvert to properly function",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);
const startedAt = performance.now();

if(["crystalsummit", "lostcrag"].includes(Deno.hostname()))
{
	xlog.info`Building programs & formats...`;
	await runUtil.run("deno", runUtil.denoArgs(path.join(xu.dirname(import.meta), "..", "..", "build", "build.js"), "programs", "formats"), runUtil.denoRunOpts({liveOutput : true}));

	await ["format", "program"].parallelMap(async type =>
	{
		let rebuilding = false;
		let dirty = false;
		const rebuildType = async line =>
		{
			if(line.endsWith(`${type}s.js`) || dirty)
				return;

			if(rebuilding)
			{
				dirty = true;
				return;
			}

			rebuilding = true;
			xlog.info`Change detected with ${type} rebuilding...`;
			(await Deno.create(`/mnt/ram/dexvert/rebuilding-${type}`)).close();
			await runUtil.run("deno", runUtil.denoArgs(path.join(xu.dirname(import.meta), "..", "..", "build", "build.js"), `${type}s`), runUtil.denoRunOpts());
			await fileUtil.unlink(`/mnt/ram/dexvert/rebuilding-${type}`);
			rebuilding = false;
			xlog.info`${type} has been rebuilt.`;

			if(dirty)
			{
				dirty = false;
				return rebuildType();
			}
		};

		await runUtil.run("inotifywait", ["-mr", "-e", "create", "-e", "delete", "-e", "moved_from", "-e", "moved_to", path.join(xu.dirname(import.meta), "..", type)], {detached : true, stdoutcb : rebuildType});
		xlog.info`Listening for any changes to src/${type} files and rebuilding if any are found.`;
	});
}

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";
const DEXSERVER_PID_FILE_PATH = path.join(DEXVERT_RAM_DIR, "dexserver.pid");
const SERVER_ORDER = ["siegfried", "tensor", "qemu"];

const servers = Object.fromEntries(await SERVER_ORDER.parallelMap(async serverid => [serverid, (await import(path.join(xu.dirname(import.meta), `../server/${serverid}.js`)))[serverid].create(xlog)]));

if(await fileUtil.exists(DEXSERVER_PID_FILE_PATH))
{
	xlog.info`Killing previous dexserver instance...`;
	const prevDexservPID = await fileUtil.readTextFile(DEXSERVER_PID_FILE_PATH);
	await runUtil.run("kill", [prevDexservPID]);
	await fileUtil.unlink(DEXSERVER_PID_FILE_PATH);
}

xlog.info`Cleaning up previous dexvert RAM installation...`;
await fileUtil.unlink(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

async function stopDexserver(sig)
{
	if(sig)
		xlog.info`Got signal ${sig}`;

	xlog.info`Stopping ${Object.keys(servers).length} servers...`;
	for(const serverid of SERVER_ORDER.reverse())
	{
		xlog.info`Stopping server ${fg.peach(serverid)}...`;
		try
		{
			await servers[serverid].stop();
		}
		catch {}
		xlog.info`Server ${fg.peach(serverid)} stopped.`;
	}
	
	await fileUtil.unlink(DEXSERVER_PID_FILE_PATH);
	xlog.info`Exiting...`;
	Deno.exit(0);
}
["SIGINT", "SIGTERM"].map(v => Deno.addSignalListener(v, async () => await stopDexserver(v)));

xu.waitUntil(async () =>
{
	if(!(await fileUtil.exists("/mnt/ram/tmp/stopdexserver")))
		return false;
	
	await fileUtil.unlink("/mnt/ram/tmp/stopdexserver", {recursive : true});
	await stopDexserver();
}, {interval : xu.SECOND*2});

xlog.info`Starting ${Object.keys(servers).length} servers...`;
for(const serverid of SERVER_ORDER)
{
	const server = servers[serverid];
	xlog.info`Starting server ${fg.peach(serverid)}...`;
	await server.start();
	xlog.info`Server ${fg.peach(serverid)} started, waiting for fully loaded...`;
	await xu.waitUntil(async () => (await server.status())===true);
	xlog.info`Server ${fg.peach(serverid)} fully loaded!`;
}

await fileUtil.writeTextFile(DEXSERVER_PID_FILE_PATH, `${Deno.pid}`);
xlog.info`\nServers fully loaded! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

while(true)
	await delay(xu.MONTH);
