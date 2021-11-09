/*
import {Program} from "../../Program.js";

export class DirMaster extends Program
{
	website = "https://style64.org/dirmaster";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website : "https://style64.org/dirmaster"
};

exports.qemu = () => "DirMaster.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => (["--exportall", inPath]);
exports.qemuData = (state, p, r) => ({osid : "winxp", cwd : "c:\\out", inFilePaths : [r.args.last()]});

exports.post = (state, p, r, cb) =>
{
	// DirMaster adds .prg extension to pretty much every file, which is kinda excessive. Let's strip it out so we can match against the real extensions
	tiptoe(
		function findPRGOutputFiles()
		{
			fileUtil.glob(state.output.absolute, "*.prg", this);
		},
		function stripPRGExtension(prgFilePaths)
		{
			prgFilePaths.parallelForEach((prgFilePath, subcb) =>
			{
				let newFilePath = prgFilePath.substring(0, prgFilePath.length-(".prg".length));

				// Often the extension is leading the filename, such as rpm.still.life
				// So we check to see if we have a 1 to 3 character extensions at the start of the file and if so, we move it to the end instead
				// This is done because some file formats (such as runPaint) rely on a proper extension
				const parts = (path.basename(newFilePath).match(/^(?<ext>\w{1,3}\.).+$/) || {groups : {}}).groups;
				if(parts.ext)
					newFilePath = path.join(path.dirname(newFilePath), `${path.basename(newFilePath).substring(parts.ext.length)}.${parts.ext.slice(0, -1)}`);
				fs.rename(prgFilePath, newFilePath, subcb);
			}, this);
		},
		cb
	);
};
*/
