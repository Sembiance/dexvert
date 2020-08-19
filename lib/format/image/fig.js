"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "XFig",
	website : "http://fileformats.archiveteam.org/wiki/Fig",
	ext     : [".fig"],
	magic   : ["FIG image text", "FIG vector drawing"],
	notes   : "It's a vector format, but embedded bitmaps don't convert to SVG. So we convert to both SVG and PNG."
};

exports.steps = [
	() => ({program : "fig2dev"}),
	(state, p) => { state.fig2devType = "png"; return p.util.flow.noop; },
	() => ({program : "fig2dev"}),
	(state, p) => { delete state.convertExt; return p.util.flow.noop; }
];
