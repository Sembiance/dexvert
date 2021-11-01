"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/hidekatsu-izuno/wmf2svg",
	gentooPackage : "media-gfx/wmf2svg",
	gentooOverlay : "dexvert",
	notes         : "This is NOT the wmf2svg provided by libwmf which doesn't work as well"
};

exports.bin = () => "/opt/bin/wmf2svg";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.svg")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.svg"), path.join(state.output.absolute, `${state.input.name}.svg`))(state, p, cb);
