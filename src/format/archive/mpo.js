"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Multi-Picture Format",
	website   : "http://fileformats.archiveteam.org/wiki/Multi-Picture_Format",
	ext       : [".mpo"],
	magic     : ["JPEG image data"],
	weakMagic : true,
	mimeType  : "image/x-mpo"
};

exports.converterPriorty = ["deark"];
