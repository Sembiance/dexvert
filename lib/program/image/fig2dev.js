"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.xfig.org/",
	gentooPackage : "media-gfx/transfig"
};

exports.bin = () => "fig2dev";
exports.args = (state, p, r, inPath=state.input.base, outPath=path.join(state.output.dirPath, `outfile.${state.fig2devType || "svg"}`)) => (["-L", (state.fig2devType || "svg"), inPath, outPath]);

// We run in the input dir in order to 'pull in' any referenced/embedded images
exports.cwd = state => state.input.dirPath;

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile.${state.fig2devType || "svg"}`), path.join(state.output.absolute, `${state.input.name}.${state.fig2devType || "svg"}`))(state, p, cb);

