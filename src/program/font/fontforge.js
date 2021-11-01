"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://fontforge.org",
	gentooPackage  : "media-gfx/fontforge",
	gentooUseFlags : "X gif gtk jpeg png python readline svg tiff unicode"
};

// Script API: https://fontforge.org/docs/scripting/python/fontforge.html
exports.bin = () => "fontforge";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile.${state.fontforgeFormat || "otf"}`)) => (["-c", `import fontforge;fontforge.open("${inPath}").generate("${outPath}")`]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile.${state.fontforgeFormat || "otf"}`), path.join(state.output.absolute, `${state.input.name}.${state.fontforgeFormat || "otf"}`))(state, p, cb);
