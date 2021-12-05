import {Program} from "../../Program.js";

export class dumpamos extends Program
{
	website       = "https://github.com/kyz/amostools/";
	package = "dev-lang/amostools";
	bin           = "dumpamos";
	cwd           = r => r.outDir();
	args          = r => [r.inFile()]
}


/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/kyz/amostools/",
	package : "dev-lang/amostools",
};

exports.bin = () => "dumpamos";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.cwd = state => state.output.absolute;
*/
