"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Kodak Photo CD",
	website  : "http://fileformats.archiveteam.org/wiki/Photo_CD",
	ext      : [".pcd"],
	mimeType : "image/x-photo-cd",
	magic    : [/Kodak Photo CD [Ii]mage/, "Kodak PhotoCD bitmap"]
};

exports.converterPriorty = ["convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
