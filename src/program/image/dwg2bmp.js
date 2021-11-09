/*
import {Program} from "../../Program.js";

export class dwg2bmp extends Program
{
	website = "https://qcad.org/en/";
	gentooPackage = "media-gfx/qcad-professional";
	gentooOverlay = "dexvert";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://qcad.org/en/",
	gentooPackage  : "media-gfx/qcad-professional",
	gentooOverlay  : "dexvert"
};

exports.bin = () => "dwg2bmp";
exports.runOptions = () => ({virtualX : true});
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.cwd, "outfile.bmp")) => (["-quality=100", `-outfile=${outPath}`, inPath]);
exports.post = (state, p, r, cb) => p.util.program.run("convert", {argsd : [path.join(state.cwd, "outfile.bmp")]})(state, p, cb);
*/
