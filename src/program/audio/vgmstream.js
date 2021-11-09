/*
import {Program} from "../../Program.js";

export class vgmstream extends Program
{
	website = "https://github.com/vgmstream/vgmstream";
	gentooPackage = "media-sound/vgmstream-cli";
	gentooOverlay = "dexvert";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/vgmstream/vgmstream",
	gentooPackage : "media-sound/vgmstream-cli",
	gentooOverlay : "dexvert"
};

exports.bin = () => "vgmstream-cli";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["-o", outPath, "-i", inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
*/
