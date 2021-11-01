"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Valve Texture Format",
	website  : "http://fileformats.archiveteam.org/wiki/Valve_Texture_Format",
	ext      : [".vtf"],
	mimeType : "image/vnd.valve.source.texture",
	magic    : ["Valve Texture Format"]
};

exports.converterPriority = ["abydosconvert"];
