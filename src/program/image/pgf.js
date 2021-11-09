/*
import {Program} from "../../Program.js";

export class pgf extends Program
{
	website = "https://www.libpgf.org/";
	gentooPackage = "media-gfx/libpgf-tools";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://www.libpgf.org/",
	gentooPackage  : "media-gfx/libpgf-tools"
};

exports.bin = () => "pgf";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => (["-d", inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
*/
