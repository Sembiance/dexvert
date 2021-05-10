"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://www.imagemagick.org/",
	gentooPackage  : "media-gfx/imagemagick",
	gentooUseFlags : "X bzip2 cxx fontconfig fpx heif jbig jpeg jpeg2k lzma openmp png postscript svg tiff truetype webp wmf xml zlib",
	informational  : true
};

exports.bin = () => "identify";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
