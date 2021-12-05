/*
import {Program} from "../../Program.js";

export class seq2mp4 extends Program
{
	website = "https://github.com/Sembiance/seq2mp4";
	package = "media-gfx/seq2mp4";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/seq2mp4",
	package : "media-gfx/seq2mp4",
	unsafe   : true
};

exports.bin = () => "seq2mp4";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.mp4")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.mp4"), path.join(state.output.absolute, `${state.input.name}.mp4`))(state, p, cb);
*/
