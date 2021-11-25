import {Program} from "../../Program.js";

export class sldtoppm extends Program
{
	website        = "http://netpbm.sourceforge.net/";
	gentooPackage  = "media-libs/netpbm";
	gentooUseFlags = "X jbig jpeg png postscript rle tiff xml zlib";
	bin            = "sldtoppm";
	args           = r => [r.inFile()];
	runOptions     = async r => ({stdoutFilePath : await r.outFile("out.ppm")});
	chain          = "convert";
}


/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "http://netpbm.sourceforge.net/",
	gentooPackage  : "media-libs/netpbm",
	gentooUseFlags : "X jbig jpeg png postscript rle tiff xml zlib"
};

exports.bin = () => "sldtoppm";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.ppm`);
*/
