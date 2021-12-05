/*
import {Program} from "../../Program.js";

export class texi2html extends Program
{
	website = "http://www.nongnu.org/texi2html/";
	package = "app-text/texi2html";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://www.nongnu.org/texi2html/",
	package : "app-text/texi2html",
	unsafe        : true
};

exports.bin = () => "texi2html";
exports.cwd = state => state.output.absolute;
exports.args = (state, p, r, inPath=state.input.filePath) => (["--l2h-tmp", state.cwd, "--l2h-clean", inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "in.html"), path.join(state.output.absolute, `${state.input.name}.html`))(state, p, cb);
*/
