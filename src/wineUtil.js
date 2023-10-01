import {xu, fg} from "xu";
import {path, delay} from "std";
import {runUtil, fileUtil} from "xutil";

export const WINE_WEB_HOST = "127.0.0.1";
export const WINE_WEB_PORT = 17737;
export const WINESERVER_VNC_BASE_PORT = 9940;

export const WINE_PREFIX_SRC = path.join(xu.dirname(import.meta), "..", "wine");
export const WINE_PREFIX = "/mnt/ram/dexvert/wine";

// For some reason I can't get capital letters to appear in wine apps when running in a virtual xvfb display screen so we do this
// TODO: Need to determine if this is just console apps or ALL apps
const CAPITAL_KEY_REPLACEMENTS =
{
	"~" : "grave",
	"!" : "1",
	"@" : "2",
	"#" : "3",
	"$" : "4",
	"%" : "5",
	"^" : "6",
	"&" : "7",
	"*" : "8",
	"(" : "9",
	")" : "0",
	"_" : "minus",
	"+" : "equal",
	"{" : "bracketleft",
	"}" : "bracketright",
	"|" : "backslash",
	'"' : "apostrophe",
	"<" : "comma",
	">" : "period",
	"?" : "slash",
	":" : "semicolon"
};

for(const c of "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split(""))
	CAPITAL_KEY_REPLACEMENTS[c] = `${c.toLowerCase()}`;

// Key names: /usr/include/X11/keysymdef.h
export async function run({f, cmd, args=[], cwd, arch="win32", base="base", console, noAuxFiles, script=[], timeout=xu.MINUTE*5, xlog})
{
	const wineBaseEnv = await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getBaseEnv`)).json();
	if(!Object.keys(wineBaseEnv).includes(base))
		throw new Error(`Invalid wine base '${base}' for cmd [${cmd}] valid bases: [${Object.keys(wineBaseEnv).join("], [")}]`);

	const cDriveDirPath = path.join(wineBaseEnv[base].WINEPREFIX, "drive_c");

	const runOptions = {detached : true, env : {...wineBaseEnv[base], WINEARCH : arch}, cwd, timeout, xlog};
	if(xlog.atLeast("trace"))
	{
		runOptions.env.DISPLAY = ":0";
	}
	else
	{
		runOptions.virtualX = true;
		runOptions.virtualXVNCPort = true;
	}

	const prelog = `wine ${fg.orange(base)} ${fg.yellow(cmd)}${fg.cyan(":")}`;

	// copy any files to our c:\in dir
	const inFiles = f ? [f.input] : [];
	if(f && !noAuxFiles)
		inFiles.push(...(f.files.aux || []));

	const prefixInDirPath = path.join(cDriveDirPath, "in");
	await fileUtil.unlink(prefixInDirPath, {recursive : true});
	await Deno.mkdir(prefixInDirPath, {recursive : true});

	const prefixOutDirPath = path.join(cDriveDirPath, "out");
	await fileUtil.unlink(prefixOutDirPath, {recursive : true});
	await Deno.mkdir(prefixOutDirPath, {recursive : true});

	xlog.debug`${prelog} Copying ${inFiles.length} files to c:\\in...`;
	for(const inFile of inFiles)
		await Deno.copyFile(inFile.absolute, path.join(prefixInDirPath, path.basename(inFile.absolute)));

	xlog.info`${prelog} Launching: ${fg.orange(cmd)} ${args.join(" ")}`;
	xlog.debug`${prelog} wine runOptions: ${runOptions}`;

	cmd = (/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`;
	
	const {cb, p, xvfbPort, virtualXVNCPort} = await runUtil.run(console ? "wineconsole" : "wine", [cmd, ...args], runOptions);

	xlog.debug`${prelog} wine launched with pid ${fg.orange(p.pid)}${virtualXVNCPort ? ` (VNC Port: ${virtualXVNCPort})` : ""}...`;
	/*if(virtualXVNCPort)
	{
		await runUtil.run("vncviewer", [`localhost:${virtualXVNCPort}`], {detached : true, env : {DISPLAY : ":0"}});
		await delay(xu.SECOND*5);
	}*/

	let failed = false;
	const scriptRunOpts = {env : { DISPLAY : xlog.atLeast("trace") ? ":0" : `:${xvfbPort}` }};
	const wids = {};
	for(const o of script)
	{
		if(typeof o==="function")
		{
			await o();
			continue;
		}

		const op = o.op;

		if(op==="windowRequire")
		{
			const {matcher, timeout : matcherTimeout=xu.SECOND*5, windowid} = o;

			let foundWID = null;
			await xu.waitUntil(async () =>
			{
				const {stdout : windowsRaw} = await runUtil.run("xwininfo", ["-root", "-tree"], scriptRunOpts);
				for(const window of windowsRaw.trim().split("\n").map(v => v.match(/^\s+(?<wid>\S+)\s+"(?<name>.+)":\s.+$/)))
				{
					const {wid, name} = window?.groups || {};
					if(!wid || !name)
						continue;

					if(matcher.test(name))
					{
						foundWID = wid;
						break;
					}
				}

				return foundWID!==null;
			}, {timeout : matcherTimeout});

			if(!foundWID)
			{
				xlog.error`${prelog} windowRequire ${windowid} failed to find a window matching ${matcher} within ${matcherTimeout}ms`;
				failed = true;
				break;
			}

			wids[windowid] = foundWID;
		}
		else if(op==="delay")
		{
			await delay(o.duration);
		}
		else if(op==="type")
		{
			const {windowid, text} = o;
			
			const textPieces = [];
			for(const textPart of text.split(/({[^}]+})/).filter(v => !!v))	// eslint-disable-line prefer-named-capture-group
			{
				const key = textPart.match(/^{(?<key>.+)}$/)?.groups?.key;
				if(key)
				{
					textPieces.push(`{${key}}`);
					continue;
				}
				
				for(const c of textPart.split(""))
					textPieces.push(CAPITAL_KEY_REPLACEMENTS[c] ? `{Shift_L+${CAPITAL_KEY_REPLACEMENTS[c]}}` : c);
			}

			const textParts = textPieces.join("").split(/({[^}]+})/).filter(v => !!v);	// eslint-disable-line prefer-named-capture-group
			let lastKey = null;
			for(const textPart of textParts)
			{
				const key = textPart.match(/^{(?<key>.+)}$/)?.groups?.key;
				if(key)
				{
					lastKey = key;
					await runUtil.run("xdotool", ["key", "--window", wids[windowid], key], scriptRunOpts);
				}
				else
				{
					await runUtil.run("xdotool", ["type", "--window", wids[windowid], textPart], scriptRunOpts);
				}
			}
			if(lastKey)
				await runUtil.run("xdotool", ["keyup", lastKey], scriptRunOpts);	// without this, the last key pressed seems to stay 'held down' if the window closes before the key is released
		}
		else
		{
			xlog.error`${prelog} Invalid script operation ${o.op} : ${o}`;
		}
	}

	if(failed)
	{
		xlog.error`${prelog} failed in some way`;
		await runUtil.run("killall", ["-9", cmd.split("\\").at(-1)], {liveOutput : true});
		await runUtil.kill(p);
	}
	
	const r = await cb();
	xlog.debug`${prelog} finished with: ${r}`;
	return r;
}
