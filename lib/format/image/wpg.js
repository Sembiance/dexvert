"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "WordPerfect Graphic",
	website : "http://fileformats.archiveteam.org/wiki/WordPerfect_Graphics",
	ext     : [".wpg"],
	magic   : ["WordPerfect Graphics bitmap", "WordPerfect graphic image"],
	notes   : "It's a vector format, but convert doesn't always properly convert it to an SVG. So we also convert it to a PNG"
};

exports.steps = [
	() => ({program : "convert"}),
	() => ({program : "convert", stateFlags : {convertExt : ".svg"}})
];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
