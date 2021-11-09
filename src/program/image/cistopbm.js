/*
import {Program} from "../../Program.js";

export class cistopbm extends Program
{
	website = "http://netpbm.sourceforge.net/";
	gentooPackage = "media-libs/netpbm";
	gentooUseFlags = "X jbig jpeg png postscript rle tiff xml zlib";
}
*/

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

exports.bin = () => "cistopbm";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.cwd, "outfile.pbm");
exports.post = (state, p, r, cb) => p.util.program.run("convert", {argsd : ["outfile.pbm"]})(state, p, cb);
*/
