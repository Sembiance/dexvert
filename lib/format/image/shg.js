"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name     : "Segmented Hypergraphics Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/Segmented_Hypergraphics",
	ext      : [".shg"],
	magic    : ["Segmented Hypergraphics bitmap"]
};

// deark on this format always converts to BMP, so we go ahead and convert that into a PNG
exports.steps =
[
	() => ({program : "deark"}),
	state => ({program : "convert", args : [path.join(state.output.dirPath, `${state.input.name}.000.bmp`), "-strip", path.join(state.output.dirPath, "outfile.png")]}),
	(state, p) => p.util.file.unlink(path.join(state.output.absolute, `${state.input.name}.000.bmp`))
];

