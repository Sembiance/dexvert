"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.gnu.org/software/libredwg/",
	gentooPackage : "media-gfx/libredwg"
};

exports.bin = () => "dwg2SVG";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.svg`);
