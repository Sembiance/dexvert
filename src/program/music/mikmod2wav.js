/*
import {Program} from "../../Program.js";

export class mikmod2wav extends Program
{
	website = "https://github.com/Sembiance/mikmod2wav";
	gentooPackage = "media-sound/mikmod2wav";
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
	website       : "https://github.com/Sembiance/mikmod2wav",
	gentooPackage : "media-sound/mikmod2wav",
	gentooOverlay : "dexvert",
	unsafe   : true
};

exports.bin = () => "mikmod2wav";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["--limitSeconds", "900", inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
*/
