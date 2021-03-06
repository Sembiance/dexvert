"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Portable Arbitrary Map",
	website  : "http://fileformats.archiveteam.org/wiki/PAM",
	ext      : [".pam"],
	mimeType : "image/x-portable-arbitrarymap",
	magic    : ["Portable Arbitrary Map bitmap", "Portable Any Map", "Netpbm PAM image file"]
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
