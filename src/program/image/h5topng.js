/*
import {Program} from "../../Program.js";

export class h5topng extends Program
{
	website = "https://github.com/NanoComp/h5utils/";
	gentooPackage = "sci-misc/h5utils";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/NanoComp/h5utils/",
	gentooPackage : "sci-misc/h5utils"
};

exports.bin = () => "h5topng";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => (["-o", outPath, "-c", "gray", inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
*/
