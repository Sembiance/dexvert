/*
import {Program} from "../../Program.js";

export class xpstopdf extends Program
{
	website = "https://wiki.gnome.org/Projects/libgxps";
	package = "app-text/libgxps";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://wiki.gnome.org/Projects/libgxps",
	package  : "app-text/libgxps",
};

exports.bin = () => "xpstopdf";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "out.pdf")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.pdf"), path.join(state.output.absolute, `${state.input.name}.pdf`))(state, p, cb);
*/
