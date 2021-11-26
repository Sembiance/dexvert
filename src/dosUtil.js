import {xu, fg} from "xu";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";
import {FileSet} from "./FileSet.js";
import {Program} from "./Program.js";
const DOS_SRC_PATH = path.join(xu.dirname(import.meta), "..", "dos");
const LOWERCASE = [null, "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "Escape", "Tab", "Backspace", "Enter", " ", "LeftAlt", "RightAlt", "LeftControl", "RightControl", "LeftShift", "RightShift", "CapsLock", "ScrollLock", "NumLock", "`", "-", "=", "\\", "[", "]", ";", '"', ".", ",", "/", null, "PrintScreen", "Pause", "Insert", "Home", "PageUp", "Delete", "End", "PageDown", "Left", "Up", "Down", "Right", "KP1", "KP2", "KP3", "KP4", "KP5", "KP6", "KP7", "KP8", "KP9", "KP0", "KPDivide", "KPMultiply", "KPMinus", "KPPlus", "KPEnter", "KPPeriod"];	// eslint-disable-line max-len
const UPPERCASE = [null, "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Z", "X", "C", "V", "B", "N", "M", null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, "~", "_", "+", "|", "{", "}", ":", "'", "<", ">", "?"];	// eslint-disable-line max-len

export async function run({cmd, args=[], root, autoExec, postExec, timeout=xu.MINUTE, screenshot, video, runIn, keys, keyOpts={}})
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
		"E:"];
	
	function addBin(bin)
	{
		if(keys)
			bootExecLines.push("SLEEP 1", "Z:\\SCRIPT.COM");

		// if we want video or a screenshot and autoexec is not handling starting the video recording itself, then start video recording
		if((video || screenshot) && !(autoExec || []).includes("VIDREC.COM start"))
			bootExecLines.push("SLEEP 1", "Z:\\VIDREC.COM start");

		bootExecLines.push(...Array.force(autoExec || bin));
		if(postExec)
			bootExecLines.push(...Array.force(postExec));

		// if we want video or a screenshot and autoexec isn't handling stopping the video recording itself, stop it here
		if((video || screenshot) && !(autoExec || []).includes("VIDREC.COM stop"))
			bootExecLines.push("Z:\\VIDREC.COM stop");
	}

	if(runIn==="prog")
	{
		bootExecLines.push(`CD ${path.relative(root, path.join(dosDirPath, path.dirname(cmd))).replaceAll("/", "\\")}`);
		addBin(`${path.basename(cmd)} ${args.join(" ")}`);
	}
	else if(runIn==="out")
	{
		bootExecLines.push(`CD OUT`);
		addBin(`..\\${path.basename(dosDirPath)}\\${cmd.replaceAll("/", "\\")} ${args.join(" ")}`);
	}
	else
	{
		addBin(`${path.basename(dosDirPath)}\\${cmd.replaceAll("/", "\\")} ${args.join(" ")}`);
	}
	
	bootExecLines.push("REBOOT.COM");	// this causes dosbox to exit, not reboot, which is what we want

	await fileUtil.writeFile(configFilePath, bootExecLines.join("\n"), "utf-8", {append : true});

	const runOptions = {liveOutput : xu.verbose>=4, timeout};
	runOptions.env = xu.verbose>=6 ? {DISPLAY : ":0"} : {SDL_VIDEODRIVER : "dummy"};

	if(keys)
	{
		const scriptEnv = [];
		let ms = (keyOpts.delay || xu.SECOND*5);
		for(const key of Array.force(keys))
		{
			if(Object.isObject(key) && key.delay)
			{
				ms += key.delay;
				continue;
			}

			for(const letter of (Array.isArray(key) ? key : key.split("")))
			{
				const keyid = UPPERCASE.includes(letter) ? UPPERCASE.indexOf(letter) : LOWERCASE.indexOf(letter);
				if(keyid===-1)
					throw new Error(`Invalid dos script key ${fg.yellow(letter)} for cmd ${cmd}`);

				if(UPPERCASE.includes(letter))
				{
					scriptEnv.push(ms);
					scriptEnv.push(LOWERCASE.indexOf("LeftShift"));
					scriptEnv.push(1);

					ms+=5;
				}

				scriptEnv.push(ms);
				scriptEnv.push(keyid);
				scriptEnv.push(1);

				ms+=10;

				scriptEnv.push(ms);
				scriptEnv.push(keyid);
				scriptEnv.push(0);

				if(UPPERCASE.includes(letter))
				{
					ms += 5;

					scriptEnv.push(ms);
					scriptEnv.push(LOWERCASE.indexOf("LeftShift"));
					scriptEnv.push(0);
				}

				ms+=100;
			}

			runOptions.env.SCRIPT = `${scriptEnv.join(",")},`;
		}
	}

	xu.log3`DOS ${fg.orange(cmd)} launching ${fg.peach("dosbox")}...`;
	const r = await runUtil.run("dosbox", ["-conf", configFilePath], runOptions);

	if(video || screenshot)
	{
		const videoFilePath = ((await fileUtil.tree(dosDirPath, {nodir : true, depth : 1, regex : /\.avi$/})) || []).sortMulti([v => v]).at(-1);
		if(!videoFilePath)
			throw new Error(`DOS no video found in ${dosDirPath} ${xu.inspect(r).squeeze()}`);
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
		
	return r;
}
