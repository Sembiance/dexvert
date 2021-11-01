"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak RAW KDC",
	website  : "http://fileformats.archiveteam.org/wiki/Kodak",
	ext      : [".kdc"],
	magic    : ["Kodak Digital Camera RAW image (DC serie)", "Kodak Digital Camera RAW image (EasyShare serie)"],
	mimeType : "image/x-kodak-kdc"
};

exports.converterPriority = ["darktable-cli", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
