/* eslint-disable require-await */
import {xu, fg} from "xu";
import {runUtil, fileUtil, webUtil, cmdUtil} from "xutil";
import {XLog} from "xlog";
import {path, delay} from "std";
import {C} from "../C.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver-wine",
	version : "1.0.0",
	desc    : "Handles running pre-launched wine instances",
	opts    :
	{
		startedFilePath : {desc : "Path to write a file to when the server has started", hasValue : true, required : true},
		stopFilePath    : {desc : "Path to watch for a file to be created to stop the server", hasValue : true, required : true},
		logLevel        : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);

const wineserverProcs = [];
const wineBaseEnv = {};
const WINE_BASES = [];
let wineCounter = 0;

const cleanupProcs = async () =>
{
	xlog.info`Killing wine procs...`;
	for(const v of ["winedevice.exe", "services.exe", "explorer.exe", "plugplay.exe", "svchost.exe", "rpcss.exe"])
		await runUtil.run("killall", ["-9", v]);
};

await cleanupProcs();

xlog.info`Preparing prefix bases...`;
await fileUtil.unlink(C.WINE_PREFIX, {recursive : true});
await Deno.mkdir(C.WINE_PREFIX, {recursive : true});

const winePrefixDirPaths = await fileUtil.tree(C.WINE_PREFIX_SRC, {nofile : true, depth : 1});
for(const winePrefixDirPath of winePrefixDirPaths)
{
	const wineBase = path.basename(winePrefixDirPath);
	WINE_BASES.push(wineBase);

	await runUtil.run("rsync", runUtil.rsyncArgs(path.join(winePrefixDirPath, "/"), path.join(C.WINE_PREFIX, wineBase, "/"), {fast : true}));
}

xlog.info`Starting wineservers...`;
for(const wineBase of WINE_BASES)
{
	const runOpts = {detached : true, stdoutcb : line => xlog.info`${xu.colon(fg.orange(wineBase))}${line}`, stderrcb : line => xlog.warn`${xu.colon(fg.orange(wineBase))}${line}`};
	runOpts.env = {WINEPREFIX : path.join(C.WINE_PREFIX, wineBase)};
	if(xlog.atLeast("debug"))
	{
		runOpts.env.DISPLAY = ":0";
	}
	else
	{
		runOpts.virtualXGLX = true;	// Required for DirectorCastRipper to work (vs just virtualX)
		runOpts.virtualXVNCPort = true;
	}

	const {p, xvfbPort, virtualXVNCPort} = await runUtil.run("wineserver", ["--foreground", "--persistent"], runOpts);
	wineserverProcs.push(p);

	wineBaseEnv[wineBase] = {DISPLAY : (runOpts.env.DISPLAY || `:${xvfbPort}`), WINEPREFIX : runOpts.env.WINEPREFIX};

	xlog.info`Wineserver ${fg.orange(wineBase)} started (DISPLAY : ${wineBaseEnv[wineBase].DISPLAY})${runOpts.virtualXVNCPort ? ` (VNC ${virtualXVNCPort})` : ""}`;
}

// Despite looking at the source code for wineserver, I couldn't find a definitive good way to determine that wineserver is 'fully loaded' and ready to go, so just sleep
await delay(xu.SECOND*3);

xlog.info`Running wineboots...`;
for(const wineBase of WINE_BASES)
{
	xlog.debug`Running wineboot for ${wineBase}...`;
	await runUtil.run("wineboot", ["--update"], {stdoutNull : true, stderrNull : true, env : wineBaseEnv[wineBase]});
}

xlog.info`Starting wine web server...`;

const routes = new Map();
routes.set("/getBaseEnv", async () => Response.json(wineBaseEnv));
routes.set("/getWineCounter", async () =>
{
	const wineCounterNum = `${wineCounter++}`;
	if(wineCounter>9000)
		wineCounter = 0;
	return new Response(wineCounterNum);
});

const webServer = webUtil.serve({hostname : C.WINE_WEB_HOST, port : C.WINE_WEB_PORT}, await webUtil.route(routes), {xlog});

xlog.debug`wineBaseEnv: ${wineBaseEnv}`;
xlog.info`Wine started`;

await fileUtil.writeTextFile(argv.startedFilePath, "");

// wait until we are told to stop
await xu.waitUntil(async () => await fileUtil.exists(argv.stopFilePath));
xlog.info`Stopping...`;
webServer.stop();

for(const wineBase of WINE_BASES)
{
	// try gracefully first
	const {timedout} = await runUtil.run("wineboot", ["--end-session", "--shutdown", "--kill", "--force"], {env : wineBaseEnv[wineBase], timeout : xu.SECOND*10});
	if(timedout)
	{
		xlog.info`Failed to cleanly stop winebase ${wineBase}, killing it...`;
		await runUtil.run("wineboot", ["--shutdown", "--kill", "--force"], {env : wineBaseEnv[wineBase], timeout : xu.SECOND*10});
	}
}

for(const p of wineserverProcs)
	await runUtil.kill(p);

xlog.debug`Deleting wine prefix bases...`;
await fileUtil.unlink(C.WINE_PREFIX, {recursive : true});

await cleanupProcs();
await fileUtil.unlink(argv.stopFilePath);
