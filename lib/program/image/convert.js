"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.imagemagick.org/",
	gentooPackage : "media-gfx/imagemagick",
	gentooUseFlags : "X bzip2 cxx fontconfig fpx heif jbig jpeg jpeg2k lzma openmp png postscript svg tiff truetype webp wmf xml zlib"
};

exports.bin = () => "convert";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile${r.flags.convertExt || ".png"}`)) => ([inPath, "-strip", "-define", "png:exclude-chunks=time", outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile${r.flags.convertExt || ".png"}`), path.join(state.output.absolute, `${state.input.name}${r.flags.convertExt || ".png"}`))(state, p, cb);
