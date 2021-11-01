"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Flash XML Graphics",
	website  : "http://fileformats.archiveteam.org/wiki/FXG",
	ext      : [".fxg"],
	magic    : ["Flash XML Graphics"],
	mimeType : "image/x-flash-xml-graphics"
};

exports.converterPriority = ["abydosconvert"];
