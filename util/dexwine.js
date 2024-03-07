import {xu} from "xu";
import {cmdUtil, fileUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";
import {run as wineRun, WINE_PREFIX_SRC, WINE_WEB_HOST, WINE_WEB_PORT} from "../src/wineUtil.js";
import {WebServer} from "WebServer";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexwine",
	version : "1.0.0",
	desc    : "Runs a program in a dex wine base prefix, to simulate it running in dexserver itself",
	opts    :
	{
		base     : {desc : "What base to use", defaultValue : "base"},
		arch     : {desc : "Which arch to use", defaultValue : "win32"},
		console  : {desc : "Run the program in a console window"},
		logLevel : {desc : "Log level to use", defaultValue : "trace"},
		program  : {desc : "Use wineData from this program", hasValue : true}
	},
	args :
	[
		{argid : "cmd", desc : "Binary to run, can be a linux path or a windows path", required : true},
		{argid : "args", desc : "Args to pass to the binary", multiple : true}
	]});

const xlog = new XLog(argv.logLevel);

const existingEnv = await xu.tryFallbackAsync(async () => await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getBaseEnv`)).json());
if(existingEnv)
	Deno.exit(xlog.error`Can't run this while dexserver is running!`);

const wineBaseEnv = {};
wineBaseEnv[argv.base] = {
	DISPLAY    : ":0",
	WINEARCH   : argv.arch,
	WINEPREFIX : path.join(WINE_PREFIX_SRC, argv.base)
};

const webServer = new WebServer(WINE_WEB_HOST, WINE_WEB_PORT, {xlog});
webServer.add("/getBaseEnv", async () => new Response(JSON.stringify(wineBaseEnv)), {logCheck : () => false});	// eslint-disable-line require-await
await webServer.start();

const wineData = {cmd : (await fileUtil.exists(argv.cmd) ? path.resolve(argv.cmd) : argv.cmd), args : argv.args || [], arch : argv.arch, base : argv.base, console : argv.console, xlog};
if(argv.program)
{
	const programModule = await import(`../program/${argv.program}.js`);
	const program = programModule[argv.program.split("/")[1]].create();
	Object.assign(wineData, (typeof program.wineData==="function" ? program.wineData({}) : program.wineData) || {});
}

await wineRun(wineData);

webServer.stop();
