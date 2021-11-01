"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Amiga Bitmap Font",
	website       : "http://fileformats.archiveteam.org/wiki/Amiga_bitmap_font",
	ext           : [".font"],
	magic         : ["Amiga bitmap Font", "AmigaOS bitmap font"],
	trustMagic    : true,
	keepFilename  : true,
	filesOptional : (state, otherFiles, otherDirs) => otherDirs.filter(otherDir => otherDir===state.input.name)
};

exports.steps = [() => ({program : "Fony"})];

