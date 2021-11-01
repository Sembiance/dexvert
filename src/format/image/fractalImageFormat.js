"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Fractal Image Format",
	website        : "http://fileformats.archiveteam.org/wiki/FIF_(Fractal_Image_Format)",
	ext            : [".fif"],
	forbidExtMatch : true,
	magic          : ["Fractal Image Format bitmap"],
	unsafe         : true,
	allowTransform : true
};

exports.converterPriority = ["fifView"];
