"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AMOS Sprites Bank",
	website  : "http://fileformats.archiveteam.org/wiki/AMOS_Sprite_Bank",
	ext      : [".abk"],
	mimeType : "image/x-amos-spritebank",
	magic    : ["AMOS Sprites Bank"]
};

// Sometimes the spite frames output are all the same size and make a nice animated image (abydosconvert does this with webp output)
// However often this format contains multiple frames of different sizes and the 'positioning' and timing information for animation is not processed
// So we also run deark which just outputs all the sprite frames individually
exports.steps = [
	() => ({program : "abydosconvert"}),
	() => ({program : "deark"})
];
