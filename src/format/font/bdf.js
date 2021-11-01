"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Glyph Bitmap Distribution Format",
	website : "http://fileformats.archiveteam.org/wiki/BDF",
	ext     : [".bdf"],
	magic   : ["X11 BDF font", "Glyph Bitmap Distribution Format font"]
};

exports.steps = [() => ({program : "bdftopcf"})];
exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
