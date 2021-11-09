/*
import {Program} from "../../Program.js";

export class fuseiso extends Program
{
	website = "https://sourceforge.net/projects/fuseiso";
	gentooPackage = "sys-fs/fuseiso";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	fs = require("fs"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://sourceforge.net/projects/fuseiso",
	gentooPackage : "sys-fs/fuseiso"
};

exports.bin = () => "fuseiso";
exports.preArgs = (state, p, r, cb) =>
{
	r.fuseisoMountDirPath = fileUtil.generateTempFilePath(state.cwd, "-fuseiso");
	fs.mkdir(r.fuseisoMountDirPath, {recursive : true}, cb);
};
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.absolute) =>
{
	r.fuseisoOutDirPath = outPath;
	return ([inPath, r.fuseisoMountDirPath]);
};

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function copyFiles()
		{
			runUtil.run("cp", ["--preserve=timestamps", "-r", "*", `"${r.fuseisoOutDirPath}/"`], {silent : true, shell : "/bin/bash", cwd : r.fuseisoMountDirPath}, this);
		},
		function unmount()
		{
			runUtil.run("fusermount", ["-u", r.fuseisoMountDirPath], runUtil.SILENT, this);
		},
		function removeMountDir()
		{
			fileUtil.unlink(r.fuseisoMountDirPath, this);
		},
		cb
	);
};
*/
