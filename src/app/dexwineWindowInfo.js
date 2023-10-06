import {xu} from "xu";
import {cmdUtil, runUtil} from "xutil";
import {WINE_WEB_HOST, WINE_WEB_PORT} from "../wineUtil.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexwineWindowInfo",
	version : "1.0.0",
	desc    : "Runs the AutoIt 3 Window Info program in a dex wine base prefix",
	opts    :
	{
		base     : {desc : "What base to use", defaultValue : "base"},
		arch     : {desc : "Which arch to use", defaultValue : "win32"},
		program  : {desc : "Use wineData from this program", hasValue : true}
	}});


const existingEnv = await xu.tryFallbackAsync(async () => await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getBaseEnv`)).json());
await runUtil.run("wine", ["c:\\Program Files\\AutoIt3\\Au3Info.exe"], {liveOutput : true, env : {WINEARCH : argv.arch, ...existingEnv[argv.base]}});

