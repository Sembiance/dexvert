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
exports.args = state => ([state.input.filePath]);
exports.runOptions = state => ({"ignore-stderr" : true, "redirect-stdout" : path.join(state.cwd, "outfile.pbm")});
exports.post = (state0, p0, cb) =>
{
	p0.util.flow.serial([
		(state, p) => p.util.program.run(p.program.convert, {args : ["outfile.pbm", ...p.program.convert.STRIP_ARGS, path.join(state.output.dirPath, "outfile.png")]}),
		(state, p) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))
	])(state0, p0, cb);
};
