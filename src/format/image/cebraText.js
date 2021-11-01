"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "CebraText",
	website  : "http://fileformats.archiveteam.org/wiki/CebraText",
	ext      : [".ttx"],
	magic    : ["Cebra Teletext page"],
	mimeType : "application/x.teletext.ttx"
};

exports.converterPriority = ["abydosconvert"];
