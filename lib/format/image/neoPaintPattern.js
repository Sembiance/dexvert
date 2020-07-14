"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "NeoPaint Pattern",
	website          : "",
	ext              : [".pat"],
	magic            : ["NeoPaint Palette"],
	weakMagic        : true,
	unsupported      : true,
	unsupportedNotes : XU.trim`
		Identified via magic as a Pallette "NeoPaint Palette" they appear to be actual "patterns" used as stamps in the MSDOS Neopaint program
		In theory I could convert these to images. Maybe opening up Neopaint, selecting the pattern, stamp it once and then save the image`
};
