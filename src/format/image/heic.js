"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "High Efficiency Image File",
	website  : "http://fileformats.archiveteam.org/wiki/HEIF",
	ext      : [".heic", ".heif"],
	mimeType : "image/heic",
	magic    : ["HEIF bitmap", "High Efficiency Image File Format", "ISO Media, HEIF Image"]
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
