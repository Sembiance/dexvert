/*
import {Program} from "../../Program.js";

export class toc2cue extends Program
{
	website = "http://cdrdao.sourceforge.net/";
	gentooPackage = "app-cdr/cdrdao";
	gentooUseFlags = "encode mad vorbis";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "http://cdrdao.sourceforge.net/",
	gentooPackage  : "app-cdr/cdrdao",
	gentooUseFlags : "encode mad vorbis"
};

exports.bin = () => "toc2cue";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.cue")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.cue"), path.join(state.output.absolute, `${state.input.name}.cue`))(state, p, cb);
*/
