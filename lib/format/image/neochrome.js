"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Neochrome",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome",
	ext      : [".neo"],
	mimeType : "image/x-neo"
};

// All Neochrome files are exactly 32,128 bytes in size (a 128 byte header followed by 32,000 bytes of image data)
exports.custom = state => (fs.statSync(state.input.absolute).size===32128);

exports.converterPriorty = ["nconvert", "abydosconvert"];
