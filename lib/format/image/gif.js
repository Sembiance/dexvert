"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Graphics Interchange Format",
	website  : "http://fileformats.archiveteam.org/wiki/GIF",
	ext      : [".gif"],
	mimeType : "image/gif",
	magic    : ["GIF image data", /^GIF8[79]a bitmap$/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedImageInputMeta(state, p, cb);
