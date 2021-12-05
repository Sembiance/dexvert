import {Program} from "../../Program.js";

export class sldtoppm extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "sldtoppm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.ppm")});
	chain      = "convert";
}


/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "http://netpbm.sourceforge.net/",
	package  : "media-libs/netpbm",
};

exports.bin = () => "sldtoppm";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.ppm`);
*/
