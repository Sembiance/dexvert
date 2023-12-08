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

if(Deno.env.get("DEX_PROD"))
	xlog.info`RUNNING IN ${xu.cf.blink("PRODUCTION")} MODE!`;

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";
const DEXSERVER_PID_FILE_PATH = path.join(DEXVERT_RAM_DIR, "dexserver.pid");
const SERVER_ORDER = ["dexrpc", "siegfried", "os", "wine", "classify"];

const servers = Object.fromEntries(await SERVER_ORDER.parallelMap(async serverid => [serverid, (await import(path.join(xu.dirname(import.meta), `../server/${serverid}.js`)))[serverid].create(xlog)]));

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

// if we don't empty this out on startup, this directory can get really big since testdexvert and testMany both write their results here instead of RAM
await fileUtil.unlink("/mnt/dexvert/test", {recursive : true});
await Deno.mkdir("/mnt/dexvert/test", {recursive : true});

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

xu.waitUntil(async () =>
{
	if(!(await fileUtil.exists("/mnt/ram/tmp/stopdexserver")))
		return false;
	
	await fileUtil.unlink("/mnt/ram/tmp/stopdexserver", {recursive : true});
	await stopDexserver();
}, {interval : xu.SECOND*2});

async function startServer(serverid)
{
	const server = servers[serverid];
	xlog.info`Starting server ${fg.peach(serverid)}...`;
	await server.start();
	xlog.info`Server ${fg.peach(serverid)} started, waiting for fully loaded...`;
	await xu.waitUntil(async () => (await server.status())===true);
	xlog.info`Server ${fg.peach(serverid)} fully loaded!`;
}

// We can't do them all at once because os/86Box is sensitive to CPU fluctuations and they won't boot properly if too much other CPU stuff is going on
xlog.info`Starting ${Object.keys(servers).length} servers...`;
for(const serverid of SERVER_ORDER)
	await startServer(serverid);

await fileUtil.writeTextFile(DEXSERVER_PID_FILE_PATH, `${Deno.pid}`);
xlog.info`\nServers fully loaded! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

while(true)
	await delay(xu.DAY);
