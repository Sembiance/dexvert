"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.ansilove.org/",
	gentooPackage : "media-gfx/ansilove",
	gentooOverlay : "dexvert",
	unsafe        : true,
	flags         :
	{
		ansiloveType : "Which ansilove format to use. Default: Let ansilove decide"
	}
};

exports.bin = () => "ansilove";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => ([...(r.flags.ansiloveType ? ["-t", r.flags.ansiloveType] : []), "-S", "-i", "-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
