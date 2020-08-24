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
exports.args = (state, p, inPath=state.input.filePath) => ([inPath]);
exports.runOptions = state => ({"ignore-stderr" : true, "redirect-stdout" : path.join(state.cwd, "outfile.pbm")});
exports.post = (state, p, cb) => p.util.program.run("convert", {args : p.program.convert.args(state, p, "outfile.pbm")})(state, p, cb);
