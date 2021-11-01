"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Imagees Music System",
	website : "http://fileformats.archiveteam.org/wiki/Images_Music_System",
	ext     : [".ims"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123", "xmp", "zxtune123"];
