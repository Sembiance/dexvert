/*
import {Program} from "../../Program.js";

export class inkscape extends Program
{
	website = "https://inkscape.org/";
	gentooPackage = "media-gfx/inkscape";
	gentooUseFlags = "cdr dbus dia exif graphicsmagick jpeg openmp postscript visio wpg";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://inkscape.org/",
	gentooPackage  : "media-gfx/inkscape",
	gentooUseFlags : "cdr dbus dia exif graphicsmagick jpeg openmp postscript visio wpg",
	unsafe         : true
};

exports.bin = () => "inkscape";
exports.runOptions = () => ({timeout : XU.MINUTE*2, virtualX : true});

// inkscape --actions="export-area-drawing; export-filename:/tmp/export.png; export-do;" inputFile
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.svg")) => (["--export-area-drawing", "--export-plain-svg", "--export-type=svg", "-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.svg"), path.join(state.output.absolute, `${state.input.name}.svg`))(state, p, cb);
*/
