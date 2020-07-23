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
exports.args = state => ([state.input.filePath, "-strip", path.join(state.output.dirPath, "outfile.png")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
