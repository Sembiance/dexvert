"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak FlashPix",
	website  : "http://fileformats.archiveteam.org/wiki/FPX",
	ext      : [".fpx"],
	mimeType : "image/vnd.fpx",
	magic    : ["Generic OLE2", "Composite Document File", "OLE2 Compound Document Format"]
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
