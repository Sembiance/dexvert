/*
import {Program} from "../../Program.js";

export class dvi2pdf extends Program
{
	website = "http://tug.org/texlive/";
	gentooPackage = "app-text/texlive";
	gentooUseFlags = "X cjk extra graphics metapost png texi2html truetype xetex xml";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "http://tug.org/texlive/",
	gentooPackage  : "app-text/texlive",
	gentooUseFlags : "X cjk extra graphics metapost png texi2html truetype xetex xml",
	unsafe         : true
};

exports.bin = () => "dvips";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.cwd, "outfile.pdf")) => (["-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.program.run("ps2pdf", {argsd : [path.join(state.cwd, "outfile.pdf")]})(state, p, cb);
*/
