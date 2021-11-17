import {xu, fg} from "xu";
import {fileUtil, runUtil} from "xutil";
import * as path from "https://deno.land/std@0.114.0/path/mod.ts";
import {delay} from "https://deno.land/std@0.114.0/async/mod.ts";
import {FileSet} from "./FileSet.js";
import {Program} from "./Program.js";
const DOS_SRC_PATH = path.join(xu.dirname(import.meta), "..", "dos");

export async function run({cmd, args=[], root, autoExec, timeout=xu.MINUTE, screenshot, video, runIn, keys, keyOpts={}})
{
	const dosDirPath = (await fileUtil.exists(path.join(root, "dos")) ? (await fileUtil.genTempPath(root, "dos")) : path.join(root, "dos"));
	await Deno.mkdir(dosDirPath);

	await runUtil.run("rsync", ["-a", path.join(DOS_SRC_PATH, (cmd.includes("/") ? path.dirname(cmd) : cmd)), path.join(dosDirPath)]);
	await runUtil.run("rsync", ["-a", path.join(DOS_SRC_PATH, "c"), path.join(dosDirPath)]);

	const configFilePath = await fileUtil.genTempPath(root, ".conf");
	await Deno.copyFile(path.join(DOS_SRC_PATH, "dosbox.conf"), configFilePath);
	await fileUtil.searchReplace(configFilePath, "captures = capture", `captures = ${dosDirPath}`);

	const bootExecLines = [
		`mount C ${path.join(dosDirPath, "c")}`,
		"PATH C:\\DOS",
		"SET TEMP=C:\\TMP",
		"SET TMP=C:\\TMP",
		"C:\\CTMOUSE\\CTMOUSE /3",
		`mount E ${root}`,
		"E:",
		`COPY NUL ${path.basename(dosDirPath)}\\STARTED.UP`];
	
	function addBin(bin)
	{
		// if we want video or a screenshot and autoexec is not handling starting the video recording itself, then start video recording
		if((video || screenshot) && !(autoExec || []).includes("VIDREC.COM start"))
			bootExecLines.push("VIDREC.COM start");

		bootExecLines.push(...Array.force(autoExec || bin));

		// if we want video or a screenshot and autoexec isn't handling stopping the video recording itself, stop it here
		if((video || screenshot) && !(autoExec || []).includes("VIDREC.COM stop"))
			bootExecLines.push("VIDREC.COM stop");
	}

	if(runIn==="prog")
	{
		bootExecLines.push(`cd ${path.relative(root, path.join(dosDirPath, path.dirname(cmd))).replaceAll("/", "\\")}`);
		addBin(`${path.basename(cmd)} ${args.join(" ")}`);
	}
	else if(runIn==="out")
	{
		// TODO Add "out" support
	}
	else
	{
		addBin(`${path.basename(dosDirPath)}\\${cmd.replaceAll("/", "\\")} ${args.join(" ")}`);
	}
	
	// this will actualy cause dosbox to exit
	bootExecLines.push("REBOOT.COM");

	await fileUtil.writeFile(configFilePath, bootExecLines.join("\n"), "utf-8", {append : true});

	const runOptions = {detached : true, liveOutput : xu.verbose>=4, timeout};
	if(xu.verbose>=6)
		runOptions.env = {DISPLAY : ":0"};
	else
		runOptions.virtualX = true;

	xu.log3`DOS ${fg.orange(cmd)} launching ${fg.peach("dosbox")}...`;

	const {p, xvfbPort} = await runUtil.run("dosbox", ["-conf", configFilePath], runOptions);
	let status = null;
	p.status().then(v => { status = v; });

	if(keys)
	{
		await xu.waitUntil(async () => !!(await fileUtil.exists(path.join(dosDirPath, "STARTED.UP"))), {timeout});
		const initialDelay = (keyOpts.delay || xu.SECOND*5);
		xu.log3`DOS ${fg.orange(cmd)} waiting ${(initialDelay/xu.SECOND)} seconds before sending keys...`;
		await xu.waitUntil(() => !!status, {timeout : initialDelay});

		for(const key of Array.force(keys))
		{
			if(status)
				break;
			
			if(Object.isObject(key) && key.delay)
			{
				xu.log3`DOS ${fg.orange(cmd)} waiting ${key.delay}ms on key delay...`;
				await delay(key.delay);
				continue;
			}

			xu.log3`DOS ${fg.orange(cmd)} sending key ${key}...`;
			const xdotoolOptions = {verbose : xu.verbose>=5, liveOutput : xu.verbose>=5, timeout, env : {"DISPLAY" : `:${xvfbPort}`}};
			await runUtil.run("xdotool", ["search", "--class", "dosbox", "windowfocus", Array.isArray(key) ? "key" : "type", "--delay", "100", Array.isArray(key) ? key[0] : key], xdotoolOptions);

			if(keyOpts.interval)
				await delay(keyOpts.interval);
		}
	}

	await xu.waitUntil(() => !!status, {timeout});

	if(video || screenshot)
	{
		const videoFilePath = ((await fileUtil.tree(dosDirPath, {nodir : true, depth : 1, regex : /\.avi$/})) || []).sortMulti([v => v]).at(-1);
		if(screenshot)
		{
			const {stdout : frameCountRaw} = await runUtil.run("ffprobe", ["-v", "0", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", videoFilePath]);
			await runUtil.run("ffmpeg", ["-i", videoFilePath, "-filter_complex", `select='eq(n,${Math.round(screenshot.frameLoc.scale(0, 100, 0, (+frameCountRaw.trim())-1))})'`, "-vframes", "1", screenshot.filePath]);
		}
		else
		{
			await Program.runProgram("ffmpeg", await FileSet.create({root, input : videoFilePath, outFile : video}), {flags : {outType : "mp4"}});
		}
	}
		
	return status;
}
