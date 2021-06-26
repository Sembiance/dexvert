"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://sk1project.net/uc2/",
	gentooPackage : "media-gfx/uniconvertor",
	gentooOverlay : "dexvert",
	flags          :
	{
		uniconvertorExt : `Which extension to convert to (".svg", ".png"). Default: .svg`
	}
};

exports.bin = () => "uniconvertor";

exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile${r.flags.uniconvertorExt || ".svg"}`)) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile${r.flags.uniconvertorExt || ".svg"}`), path.join(state.output.absolute, `${state.input.name}${r.flags.uniconvertorExt || ".svg"}`))(state, p, cb);
