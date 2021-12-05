/*
import {Program} from "../../Program.js";

export class latex2pdf extends Program
{
	website = "http://latex2rtf.sourceforge.net/";
	package = "dev-tex/latex2rtf";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website        : "http://latex2rtf.sourceforge.net/",
	package  : "dev-tex/latex2rtf"
};

// Converts to RTF and then uses soffice to convert to PDF
exports.bin = () => "latex2rtf";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.cwd, `${state.input.name}.rtf`)) => (["-T", state.cwd, "-o", outPath, inPath]);
exports.post = (state, p, r, cb) =>
{
	const outFilePath = r.args[r.args.length-2];
	if(!fileUtil.existsSync(outFilePath))
		return setImmediate(cb);
	
	// When latex2rtf fails, it will produce a zero sized .rtf output file. soffice will happily convert this into a blank PDF, so let's get rid of it instead
	if(fs.statSync(outFilePath).size===0)
		return fileUtil.unlink(outFilePath, cb);
	
	return p.util.program.run("soffice", {argsd : [path.join(state.cwd, `${state.input.name}.rtf`)]})(state, p, cb);
};
*/
