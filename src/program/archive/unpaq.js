import {Program} from "../../Program.js";

export class unpaq extends Program
{
	website   = "http://files.mpoli.fi/unpacked/software/dos/compress/quant097.zip/";
	loc       = "dos";
	bin       = "QUANTUM/UNPAQ.EXE";
	args      = r => ["-x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}


/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://files.mpoli.fi/unpacked/software/dos/compress/quant097.zip/"
};

exports.dos = () => "QUANTUM/UNPAQ.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`..\\${inPath}`]);
exports.dosData = (state, p, r) => ({includeDir : true, autoExec : ["CD OUT", `..\\QUANTUM\\UNPAQ.EXE -x ${r.args}`]});
*/
