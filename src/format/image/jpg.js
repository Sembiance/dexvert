"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Joint Photographic Experts Group Image",
	website   : "http://fileformats.archiveteam.org/wiki/JPG",
	ext       : [".jpg", ".jpeg", ".jpe", ".jfif"],
	mimeType  : "image/jpeg",
	magic     : ["JFIF JPEG bitmap", "JPEG image data", "JPEG bitmap", "JPEG File Interchange Format"],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
