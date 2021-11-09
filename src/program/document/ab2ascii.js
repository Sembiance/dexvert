/*
import {Program} from "../../Program.js";

export class ab2ascii extends Program
{
	website = "http://aminet.net/package/dev/misc/ab2ascii-1.3";
	gentooPackage = "dev-lang/ab2ascii";
	gentooOverlay = "dexvert";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://aminet.net/package/dev/misc/ab2ascii-1.3",
	gentooPackage : "dev-lang/ab2ascii",
	gentooOverlay : "dexvert",
	unsafe   : true
};

exports.bin = () => "ab2ascii";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.txt")) => (["-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.txt"), path.join(state.output.absolute, `${state.input.name}_amigaBASIC.txt`))(state, p, cb);
*/
