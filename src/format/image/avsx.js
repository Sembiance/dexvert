"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Stardent AVS X",
	website  : "http://fileformats.archiveteam.org/wiki/AVS_X_image",
	ext      : [".avs", ".mbfavs", ".x"],
	mimeType : "image/x-avsx"
};

exports.converterPriority = ["nconvert", "abydosconvert"];
