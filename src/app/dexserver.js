import {xu, fg} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil, cmdUtil} from "xutil";
import {path, delay} from "std";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver",
	version : "1.0.0",
	desc    : "Starts needed background services for dexvert to properly function",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);

if(!Deno.env.has("daemonized"))
	Deno.exit(xlog.error`This program should only be run with startDexserver!`);

const startedAt = performance.now();

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";
const DEXSERVER_PID_FILE_PATH = path.join(DEXVERT_RAM_DIR, "dexserver.pid");
const SERVER_ORDER = ["dexrpc", "siegfried", "os", "wine", "classify"];

if(await fileUtil.exists(DEXSERVER_PID_FILE_PATH))
{
	xlog.info`Killing previous dexserver instance...`;
	const prevDexservPID = await fileUtil.readTextFile(DEXSERVER_PID_FILE_PATH);
	await runUtil.run("kill", [prevDexservPID]);
	await fileUtil.unlink(DEXSERVER_PID_FILE_PATH);
}

xlog.info`Cleaning up previous dexserver files...`;
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});
await runUtil.run("/mnt/compendium/bin/fixPerms", [], {cwd : DEXVERT_RAM_DIR});
await fileUtil.unlink(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

// we need to empty these on startup otherwise these get really big and take a lot of space
for(const dir of ["test", "sample"])
{
	await fileUtil.unlink(path.join("/mnt/dexvert", dir), {recursive : true});
	await Deno.mkdir(path.join("/mnt/dexvert", dir), {recursive : true});
}

const serverStatusDirPath = await fileUtil.genTempPath(undefined, "dexserver-serverStatus");
await Deno.mkdir(serverStatusDirPath);

const serverProcs = {};
async function stopDexserver()
{
	xlog.info`Stopping ${SERVER_ORDER.length} servers...`;
	for(const serverid of Array.from(SERVER_ORDER).reverse())
	{
		xlog.info`Stopping server ${fg.peach(serverid)}...`;
		const stopFilePath = path.join(serverStatusDirPath, `stop-${serverid}`);
		await fileUtil.writeTextFile(stopFilePath, "");
		await xu.waitUntil(async () => !await fileUtil.exists(stopFilePath), {timeout : xu.SECOND*20});
		await runUtil.kill(serverProcs[serverid]);
	}

	await fileUtil.unlink(serverStatusDirPath, {recursive : true});
	await fileUtil.unlink(DEXSERVER_PID_FILE_PATH);
	xlog.info`Exiting...`;
	Deno.exit(0);
}

xu.waitUntil(async () =>
{
	if(!await fileUtil.exists("/mnt/ram/tmp/stopdexserver"))
		return false;
	
	await fileUtil.unlink("/mnt/ram/tmp/stopdexserver", {recursive : true});
	await stopDexserver();
}, {interval : xu.SECOND*2});

// We can't do them all at once because os/86Box is sensitive to CPU fluctuations and they won't boot properly if too much other CPU stuff is going on
xlog.info`Starting ${SERVER_ORDER.length} servers...`;
for(const serverid of SERVER_ORDER)
{
	const xlogServer = xlog.clone();
	xlogServer.mapper = v => `${xu.colon(fg.peach(serverid))}${v}`;

	const startedFilePath = path.join(serverStatusDirPath, `started-${serverid}`);
	const stopFilePath = path.join(serverStatusDirPath, `stop-${serverid}`);

	xlog.info`Starting server ${fg.peach(serverid)}...`;
	const {p} = await runUtil.run("deno", runUtil.denoArgs(path.join(import.meta.dirname, "..", "server", `${serverid}.js`), `--logLevel=${argv.logLevel}`, `--stopFilePath=${stopFilePath}`, `--startedFilePath=${startedFilePath}`), runUtil.denoRunOpts({detached : true, xlog : xlogServer}));
	serverProcs[serverid] = p;
	xlog.info`Server ${fg.peach(serverid)} started, waiting for fully loaded...`;
	await xu.waitUntil(async () => (await fileUtil.exists(startedFilePath)));
	xlog.info`Server ${fg.peach(serverid)} fully loaded!`;
}

xlog.info`\nServers fully loaded! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;
await fileUtil.writeTextFile(DEXSERVER_PID_FILE_PATH, `${Deno.pid}`);

while(true)
	await delay(xu.DAY);
