import {xu} from "xu";
import {cmdUtil, runUtil} from "xutil";
import {WINE_WEB_HOST, WINE_WEB_PORT} from "../src/wineUtil.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexwineWindowInfo",
	version : "1.0.0",
	desc    : "Runs the AutoIt 3 Window Info program in a dex wine base prefix",
	opts    :
	{
		base       : {desc : "What base to use", defaultValue : "base"},
		arch       : {desc : "Which arch to use", defaultValue : "win32"},
		winSpector : {desc : "Run WinSpector instead of the window info program"},
		winSpy     : {desc : "Run WinSpy instead of the window info program"}
	}});

const existingEnv = await xu.tryFallbackAsync(async () => await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getBaseEnv`)).json());
await runUtil.run("wine", [argv.winSpy ? `c:\\dexvert\\winspy.exe` : (argv.winSpector ? "c:\\Program Files\\Winspector\\WinspectorU.exe" : "c:\\Program Files\\AutoIt3\\Au3Info.exe")], {liveOutput : true, env : {WINEARCH : argv.arch, ...existingEnv[argv.base]}});

