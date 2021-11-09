/*
import {Program} from "../../Program.js";

export class npack extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/NPack";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website : "http://fileformats.archiveteam.org/wiki/NPack",
	unsafe  : true
};

exports.dos = () => "NDFIX-1/NPACK.EXE";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "OUTFILE")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) =>
{
	const outFilePath = path.join(state.output.absolute, "OUTFILE");
	if(!fileUtil.existsSync(outFilePath))
		return setImmediate(cb);
		
	if(p.util.file.compareFileBytes(outFilePath, 0, Buffer.from([0x4D, 0x53, 0x54, 0x53, 0x4D])))
		p.util.file.unlink(outFilePath)(state, p, cb);
	else
		p.util.file.move(outFilePath, path.join(state.output.absolute, `${state.input.name}${state.input.ext.replaceAll("$", "")}`))(state, p, cb);
};
*/
