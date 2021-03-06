"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Radiance HDR",
	website  : "http://fileformats.archiveteam.org/wiki/Radiance_HDR",
	ext      : [".hdr", ".rgbe", ".xyze", ".pic", ".rad"],
	mimeType : "image/vnd.radiance",
	magic    : ["Radiance RGBE Image Format", "Radiance HDR image data", "Radiance High Dynamic Range bitmap"],
	slow     : true
};

exports.converterPriorty = ["pfsconvert", "convert", "nconvert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
