/*
import {Program} from "../../Program.js";

export class ps2pdf extends Program
{
	website = "https://ghostscript.com/";
	gentooPackage = "app-text/ghostscript-gpl";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://ghostscript.com/",
	gentooPackage : "app-text/ghostscript-gpl"
};

exports.bin = () => "ps2pdf";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.pdf")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.pdf"), path.join(state.output.absolute, `${state.input.name}.pdf`))(state, p, cb);
*/
