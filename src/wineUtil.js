import {xu, fg} from "xu";
import {path} from "std";
import {runUtil, fileUtil} from "xutil";
import {appendCommonFuncs} from "./autoItUtil.js";

export const WINE_WEB_HOST = "127.0.0.1";
export const WINE_WEB_PORT = 17737;
export const WINESERVER_VNC_BASE_PORT = 9940;

export const WINE_PREFIX_SRC = path.join(import.meta.dirname, "..", "wine");
export const WINE_PREFIX = "/mnt/ram/dexvert/wine";

export function getWineDriveC(base)
{
	return path.join(WINE_PREFIX, base, "drive_c");
}

// Key names: /usr/include/X11/keysymdef.h
// Wine Guide: https://wiki.winehq.org/Wine_User%27s_Guide
export async function run({f, cmd, args=[], cwd, arch="win32", base="base", console, keepOutput, script, wineCounter, timeout=xu.MINUTE*10, timeoutSignal="SIGTERM", xlog, monitor})
{
	const wineBaseEnv = await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getBaseEnv`)).json();
	if(!Object.keys(wineBaseEnv).includes(base))
		throw new Error(`Invalid wine base '${base}' for cmd [${cmd}] valid bases: [${Object.keys(wineBaseEnv).join("], [")}]`);

	let wineInDirPath = null;
	let wineOutDirPath = null;
	if(wineCounter!==undefined)
	{
		wineInDirPath = path.join(wineBaseEnv[base].WINEPREFIX, "drive_c", `in${wineCounter}`);
		await Deno.mkdir(wineInDirPath);

		for(const file of [f.input, ...(f.files.aux || [])])
			await Deno.copyFile(file.absolute, path.join(wineInDirPath, path.basename(file.absolute)));

		wineOutDirPath = path.join(wineBaseEnv[base].WINEPREFIX, "drive_c", `out${wineCounter}`);
		await Deno.mkdir(wineOutDirPath);
	}

	const runOptions = {detached : true, env : {...wineBaseEnv[base], WINEARCH : arch}, cwd, timeout, timeoutSignal};
	if(!keepOutput)
		runOptions.xlog = xlog;
	if(runOptions.cwd?.startsWith("wine://"))
		runOptions.cwd = path.join(wineBaseEnv[base].WINEPREFIX, "drive_c", runOptions.cwd.substring("wine://".length));

	const prelog = `wine ${fg.orange(base)} ${fg.yellow(cmd)}${fg.cyan(":")}`;

	xlog.info`${prelog} Launching: ${fg.orange(cmd)} ${args.join(" ")}`;
	xlog.debug`${prelog} wine runOptions: ${runOptions}`;

	cmd = ((/^[A-Za-z]:/).test(cmd) || cmd.startsWith("/")) ? cmd : `c:\\dexvert\\${cmd}`;
	
	const {p, cb} = await runUtil.run(console ? "wineconsole" : "wine", [cmd, ...args], runOptions);
	const monitorPromise = monitor ? monitor({p, xlog}) : null;

	if(script)
	{
		const scriptLines = [];
		appendCommonFuncs(scriptLines, {script, timeout, fullCmd : cmd, skipMouseMoving : true});
		scriptLines.push(script);

		const tmpScriptFilePath = await fileUtil.genTempPath(undefined, ".au3");
		await fileUtil.writeTextFile(tmpScriptFilePath, scriptLines.join("\n"));

		const autoItRunOptions = { env : runOptions.env};
		xlog.debug`Running AutoIt3 with script with env: ${autoItRunOptions}...`;
		await runUtil.run("wine", [`c:\\Program Files${runOptions.env.WINEARCH==="win64" ? " (x86)" : ""}\\AutoIt3\\AutoIt3${runOptions.env.WINEARCH==="win64" ? "_x64" : ""}.exe`, tmpScriptFilePath], autoItRunOptions);
		xlog.debug`AutoIt3 script finished`;

		await fileUtil.unlink(tmpScriptFilePath);
	}
	
	const r = await cb();
	if(monitorPromise)
		await monitorPromise;
	xlog.debug`${prelog} finished with: ${r}`;

	if(wineInDirPath && wineOutDirPath)
	{
		if(f.outDir)
			await runUtil.run("rsync", runUtil.rsyncArgs(path.join(wineOutDirPath, "/"), path.join(f.outDir.absolute, "/")));
		await fileUtil.unlink(wineOutDirPath, {recursive : true});
		await fileUtil.unlink(wineInDirPath, {recursive : true});
	}

	return r;
}
