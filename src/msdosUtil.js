import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import {path, delay, getAvailablePort} from "std";

const MSDOS_SRC_PATH = path.join(import.meta.dirname, "..", "msdos");
const FLOPPY_TYPES = ["360k", "720k", "1.2m", "1.44m", "2.88m"];

export async function run({cmd, args=[], root, inFile, outDir, floppy, keys, timeout=xu.MINUTE*2, xlog})
{
	const msdosDirPath = (await fileUtil.exists(path.join(root, "msdos")) ? (await fileUtil.genTempPath(root, "msdos")) : path.join(root, "msdos"));
	await Deno.mkdir(msdosDirPath);

	const floppyType = FLOPPY_TYPES.includes(floppy?.type) ? floppy.type : "1.44m";
	const floppyConfigDirPath = path.join(MSDOS_SRC_PATH, "floppy", floppyType);
	await runUtil.run("rsync", runUtil.rsyncArgs(path.join(floppyConfigDirPath, "nvr", "/"), path.join(msdosDirPath, "nvr", "/"), {inPlace : true, fast : true}));
	await Deno.copyFile(path.join(MSDOS_SRC_PATH, "hd.vhd"), path.join(msdosDirPath, "hd.vhd"));
	await Deno.copyFile(path.join(floppyConfigDirPath, "86box.cfg"), path.join(msdosDirPath, "86box.cfg"));
	await Deno.mkdir(path.join(msdosDirPath, "printer"));

	const inoutDirPath = path.join(msdosDirPath, "inout");
	await Deno.mkdir(inoutDirPath);

	const inDirPath = path.join(inoutDirPath, "IN");
	await Deno.mkdir(inDirPath);
	await Deno.copyFile(inFile.absolute, path.join(inDirPath, inFile.base));
	
	const outDirPath = path.join(inoutDirPath, "OUT");
	await Deno.mkdir(outDirPath);

	const dexvertBAT = ["@ECHO OFF"];
	dexvertBAT.push("ECHO RUN>PRN");
	dexvertBAT.push(`${cmd}${args.length ? ` ${args.join(" ")}` : ""}`);
	dexvertBAT.push("ECHO DONE>PRN");
	await fileUtil.writeTextFile(path.join(inoutDirPath, "DEXVERT.BAT"), dexvertBAT.join("\r\n"));
	const {stdout : hdSizeRaw} = await runUtil.run("deno", runUtil.denoArgs("/mnt/compendium/DevLab/apps/mkDOSHDFromFiles/mkDOSHDFromFiles.js", path.join(msdosDirPath, "inout.img"), ...(await fileUtil.tree(inoutDirPath, {depth : 1}))), runUtil.denoRunOpts());
	const hdSize = xu.parseJSON(hdSizeRaw);
	await fileUtil.unlink(inoutDirPath, {recursive : true});

	if(floppy?.filePath)
		await Deno.symlink(floppy.filePath, path.join(msdosDirPath, "floppy.img"));
	
	const runOptions = {cwd : msdosDirPath, detached : true, env : {}};
	if(xlog.atLeast("trace"))
	{
		runOptions.liveOutput = true;
		runOptions.env.DISPLAY = ":0";
		runOptions.env.EMU86BOX_MOUSE = "evdev";
	}
	else
	{
		runOptions.virtualX = true;
		runOptions.virtualXVNCPort = getAvailablePort();
	}
	
	xlog.debug`msdos for '${cmd} ${args.join(" ")}' launching 86Box in dir ${msdosDirPath} using hd ${hdSize} and run options: ${runOptions}`;
	const {p, cb, xvfbPort} = await runUtil.run("86Box", ["86box.cfg"], runOptions);

	const keyRunOptions = {env : {DISPLAY : `:${xlog.atLeast("trace") || !xvfbPort ? "0" : xvfbPort}`}};
	let wid = null;
	if(keys)
	{
		let widAttempts = 0;
		while(!wid && widAttempts<4)
		{
			await delay(xu.SECOND*3);
			const wids = ((await runUtil.run("xdotool", ["search", "--onlyvisible", "86Box"], keyRunOptions))?.stdout || "").split("\n").map(v => v.trim()).filter(v => v.length).map(v => `0x${(+v).toString(16)}`);
			if(wids.length)
			{
				wid = wids.at(-1);
				break;
			}

			widAttempts++;
		}
		if(!wid)
			xlog.error`msdos failed to find 86Box window id to send keys to after ${widAttempts} attempts with keyRunOptions: ${keyRunOptions}`;
	}

	const startedAt = performance.now();
	let done=false;
	let ran=false;
	while((performance.now()-startedAt)<timeout)
	{
		await delay(xu.SECOND);

		for(const printerFile of await fileUtil.tree(path.join(msdosDirPath, "printer"), {nodir : true, depth : 1}))
		{
			for(const line of (await fileUtil.readTextFile(printerFile))?.trim()?.split("\n") || [])
			{
				if(line.trim()==="DONE")
				{
					done = true;
					break;
				}

				if(keys && wid && !ran && line.trim()==="RUN")
				{
					xlog.trace`msdos sending keys to window ${wid} with options ${keyRunOptions} and keys: ${keys}`;
					for(const key of Array.force(keys))
					{
						if(typeof key==="number")
						{
							await delay(key);
							continue;
						}

						await runUtil.run("xdotool", ["key", "--window", wid, key], keyRunOptions, {liveOutput : xlog.atLeast("trace")});
					}

					ran = true;
				}
			}

			if(done)
				break;
		}

		if(done)
			break;
	}

	await runUtil.kill(p, "SIGKILL");
	const r = await cb();

	await Deno.mkdir(inoutDirPath);
	await runUtil.run("sudo", ["mount", "-o", `loop,offset=${hdSize.start*hdSize.sectorSize}`, path.join(msdosDirPath, "inout.img"), inoutDirPath]);
	await runUtil.run("rsync", runUtil.rsyncArgs(path.join(inoutDirPath, "OUT", "/"), path.join(outDir.absolute, "/"), {inPlace : true, fast : true}));
	await runUtil.run("sudo", ["umount", inoutDirPath]);

	if(!xlog.atLeast("trace"))
		await fileUtil.unlink(msdosDirPath, {recursive : true});

	return r;
}
