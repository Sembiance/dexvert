"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Envision Publisher Font",
	website     : "http://fileformats.archiveteam.org/wiki/Envision_Publisher",
	ext         : [".svf"],
	magic       : ["EnVision Publisher DTP Font"],
	unsupported : true,
	notes       : "Font file for the MSDOS program Envsion Publisher. Fontforge doesn't handle it and I didn't bother trying to convert further."
};
