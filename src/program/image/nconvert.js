"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.xnview.com/en/nconvert/",
	gentooPackage : "media-gfx/nconvert",
	gentooOverlay : "dexvert",
	flags :
	{
		nconvertFormat : "Which nconvert format to force conversion as. For list run `nconvert -help` Default: Let nconvert decide"
	}
};

exports.bin = () => "nconvert";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) =>
{
	const nconvertArgs = [];
	if(r.flags.nconvertFormat)
		nconvertArgs.push("-in", r.flags.nconvertFormat);
	nconvertArgs.push("-out", "png", "-o", outPath, inPath);
	return nconvertArgs;
};
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);