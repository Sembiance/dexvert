"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Game Music Creator Module",
	website : "http://fileformats.archiveteam.org/wiki/Game_Music_Creator",
	ext     : [".gmc"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123", "xmp"];
