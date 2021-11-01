"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "QRT Ray Tracer Bitmap",
	website        : "http://fileformats.archiveteam.org/wiki/QRT_Ray_Tracer_bitmap",
	ext            : [".qrt", ".dis", ".raw"],
	forbiddenMagic : ["KryoFlux raw stream"]
};

exports.converterPriority = ["nconvert"];
