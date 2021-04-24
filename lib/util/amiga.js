"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	os = require("os"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file;

function replaceHexChars(_text)
{
	let text = _text;
	const hexChars = Array.from(text.matchAll(/%(?<c>[\da-fA-F]{2})/g), v => v?.groups?.c).filterEmpty().unique();
	if(hexChars.length===0)
		return null;

	hexChars.forEach(hexChar =>
	{
		text = text.replaceAll(`%${hexChar}`, String.fromCharCode(parseInt(hexChar.toLowerCase(), 16)));
	});

	return text;
}

const AMIGA_BASE_DIR = path.join(__dirname, "..", "..", "amiga");

// WB3.1 has a S:user-startup that will EXECUTE in:dexDexScript if it exists
// For Amiga scripting help, see dev/amiga.txt
exports.run = function run({cmd, args=[], dexScript, inFilePaths=[], floppyFilePaths=[], timeout=XU.MINUTE*3})
{
	return (state, p, cb) =>
	{
		const workDirPath = fileUtil.generateTempFilePath(undefined, "-amiga");

		tiptoe(
			function createWorkDir()
			{
				fs.mkdir(path.join(workDirPath), {recursive : true}, this);
			},
			function createSubDirs()
			{
				fs.mkdir(path.join(workDirPath, "in"), {recursive : true}, this.parallel());
				fs.mkdir(path.join(workDirPath, "env"), {recursive : true}, this.parallel());
			},
			function prepareWorkDir()
			{
				fs.copyFile(path.join(AMIGA_BASE_DIR, "WB31.hdf"), path.join(workDirPath, "WB31.hdf"), this.parallel());
				fs.symlink(state.output.absolute, path.join(workDirPath, "out"), this.parallel());
				fs.writeFile(path.join(workDirPath, "config.fs-uae"), `
[config]
amiga_model = A1200/020
fast_memory = 8192
uaem_write_flags = n
floppy_drive_speed = 0
floppy_drive_0_sounds = off
floppy_drive_1_sounds = off
uae_cpu_speed = max
uae_fpu_model = 68882
fullscreen = 0
window_width = 1024
window_height = 768
fsaa = 0
scanlines = 0
graphics_card = uaegfx
scale = 0
keep_aspect = 1
video_sync = off

hard_drive_0 = ${path.join(workDirPath, "WB31.hdf")}
hard_drive_0_priority = 6
hard_drive_1 = ${path.join(workDirPath, "in")}
hard_drive_2 = ${path.join(workDirPath, "out")}

${floppyFilePaths.map((floppyFilePath, i) => `floppy_drive_${i} = ${floppyFilePath}`).join("\n")}`, XU.UTF8, this.parallel());

				// We use rsync here to handle both files and directories and preserve timestamps
				inFilePaths.map(v => (v.startsWith("/") ? v : path.resolve(state.cwd, v))).parallelForEach((v, subcb) => runUtil.run("rsync", ["-aL", v, path.join(workDirPath, "in", "/")], runUtil.SILENT, subcb), this.parallel());

				const dexScriptLines = [dexScript || `${cmd} ${args.map(v => (inFilePaths.includes(v) ? `in:${v}` : v)).join(" ")}`, "UAEquit", ""];
				fs.writeFile(path.join(workDirPath, "in", "dexScript"), dexScriptLines.join("\n"), XU.UTF8, this.parallel());

				p.util.program.run("tar", {argsd : [path.join(AMIGA_BASE_DIR, "fs-uae-env.tar"), path.join(workDirPath, "env")]})(state, p, this.parallel());

				if(state.verbose>=3)
					XU.log`Running amiga in dir ${workDirPath} dexScript ${dexScriptLines}`;
			},
			function runUAE()
			{
				const runOptions = {cwd : workDirPath, timeout};

				// fs-uae requires OpenGL, until headless comes to fs-uae v4: https://github.com/FrodeSolheim/fs-uae/issues/91
				// chatsubo is running a headless xorg and sadly Xvfb with "+extension GLX" fails with a segfault, couldn't figure out why
				// Thus on chatsubo, we just run all fs-uae programs on the dummy display which does have glx support
				if(os.hostname()==="chatsubo")
				{
					runOptions.env = {DISPLAY : ":0"};
				}
				else
				{
					runOptions.virtualX = true;
					runOptions.withGLX = true;
				}

				//if(state.verbose>=5)
				//	runOptions.recordVideoFilePath = fileUtil.generateTempFilePath(undefined, ".mp4");
				if(state.verbose>=4)
					runOptions.verbose = true;
				else
					runOptions.silent = true;

				runUtil.run("fs-uae", [`--base-dir=${path.join(workDirPath, "env")}`, "config.fs-uae"], runOptions, this);
			},
			function findOutputFiles()
			{
				fileUtil.glob(state.output.absolute, "**", this);
			},
			function renameASCIICodes(outFilePaths)
			{
				// fs-uae outputs files with %FF ascii codes for certain characters. We convert them back to ascii here
				outFilePaths.parallelForEach((outFilePath, subcb) =>
				{
					let newName = replaceHexChars(path.basename(outFilePath));
					if(!newName)
						return setImmediate(subcb);

					// On the Amiga you can encounter filenames that are just a single or a double period, which isn't gonna work under a Linux filesystem, so change the periods to bullets
					if(newName==="." || newName==="..")
						newName = newName.replaceAll(".", "•");
					
					// The forward slash is forbidden under linux for filenames, so replace it
					if(newName.includes("/"))
						newName = newName.replaceAll("/", "|");

					fs.rename(outFilePath, path.join(path.dirname(outFilePath), newName), subcb);
				}, this);
			},
			function findUAEMemFiles()
			{
				// .uaem files are produced when a file has a 'note' attached. These notes are also encoded with %FF ascii codes, so I replace the codes in them
				fileUtil.glob(state.output.absolute, "**/*.uaem", {nodir : true}, this);
			},
			function loadUAEMemFiles(uaemFilePaths)
			{
				this.data.uaemFilePaths = uaemFilePaths;

				uaemFilePaths.parallelForEach((uaemFilePath, subcb) => fs.readFile(uaemFilePath, XU.UTF8, subcb), this);
			},
			function replaceASCIICodeContent(uaemContentsRaw)
			{
				uaemContentsRaw.parallelForEach((uaemContentRaw, subcb, i) =>
				{
					const uaemContent = replaceHexChars(uaemContentRaw.toString("utf8"));
					if(!uaemContent)
						return setImmediate(subcb);

					fs.writeFile(this.data.uaemFilePaths[i], uaemContent, XU.UTF8, subcb);
				}, this);
			},
			function cleanup()
			{
				if(state.verbose>=5)
					return this();

				fileUtil.unlink(workDirPath, this);
			},
			cb
		);
	};
};
