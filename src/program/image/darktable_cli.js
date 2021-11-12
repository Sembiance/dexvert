/*
import {Program} from "../../Program.js";

export class darktable_cli extends Program
{
	website = "https://www.darktable.org/";
	gentooPackage = "media-gfx/darktable";
	gentooUseFlags = "cups jpeg2k lua nls openexr openmp webp";
	symlinkUnsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://www.darktable.org/",
	gentooPackage  : "media-gfx/darktable",
	gentooUseFlags : "cups jpeg2k lua nls openexr openmp webp",
	symlinkUnsafe  : true
};

exports.bin = () => "darktable-cli";
exports.runOptions = state => ({env : {HOME : state.cwd}});
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
*/
