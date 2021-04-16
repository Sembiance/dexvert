"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file;

// WB3.1 has a S:user-startup that will EXECUTE in:dexDexScript if it exists
// For Amiga scripting help, see dev/amiga.txt
exports.run = function run({cmd, args=[], dexScript, inFilePaths=[], timeout=XU.MINUTE*3})
{
	return (state, p, cb) =>
	{
		const workDirPath = fileUtil.generateTempFilePath(undefined, "-amiga");

		tiptoe(
			function createWorkDir()
			{
				fs.mkdir(path.join(workDirPath, "in"), {recursive : true}, this);
			},
			function prepareWorkDir()
			{
				fs.copyFile(path.join(__dirname, "..", "..", "amiga", "WB31.hdf"), path.join(workDirPath, "WB31.hdf"), this.parallel());
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

hard_drive_0 = ${path.join(workDirPath, "WB31.hdf")}
hard_drive_0_priority = 6
hard_drive_1 = ${path.join(workDirPath, "in")}
hard_drive_2 = ${path.join(workDirPath, "out")}`, XU.UTF8, this.parallel());
				// TODO: Floppy support: ${ifFloppyImage ? `floppy_drive_0 = ${floppyImageFilePath}` : ""}

				// We use rsync here to handle both files and directories and preserve timestamps
				inFilePaths.map(v => (v.startsWith("/") ? v : path.resolve(state.cwd, v))).parallelForEach((v, subcb) => runUtil.run("rsync", ["-aL", v, path.join(workDirPath, "in", "/")], runUtil.SILENT, subcb), this.parallel());

				const dexScriptLines = [dexScript || `${cmd} ${args.map(v => (inFilePaths.includes(v) ? `in:${v}` : v)).join(" ")}`, "UAEquit", ""];
				fs.writeFile(path.join(workDirPath, "in", "dexScript"), dexScriptLines.join("\n"), XU.UTF8, this.parallel());

				if(state.verbose>=3)
					XU.log`Running amiga in dir ${workDirPath} dexScript ${dexScriptLines}`;
			},
			function runUAE()
			{
				const runOptions = {cwd : workDirPath, timeout, virtualX : true};
				//if(state.verbose>=5)
				//	runOptions.recordVideoFilePath = fileUtil.generateTempFilePath(undefined, ".mp4");
				if(state.verbose>=4)
					runOptions.verbose = true;
				else
					runOptions.silent = true;

				runUtil.run("fs-uae", ["--base-dir=/mnt/compendium/DevLab/dexvert/amiga/FS-UAE", "config.fs-uae"], runOptions, this);
			},
			function findOutputFiles()
			{
				fileUtil.glob(state.output.absolute, "**", {nodir : true}, this);
			},
			function renameASCIICodes()
			{
				// TODO: Rename any file that contains %xx with the ASCII code equilivant
				this();
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
