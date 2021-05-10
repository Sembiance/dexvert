"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Portable Pixmap",
	website  : "http://fileformats.archiveteam.org/wiki/Netpbm_formats",
	ext      : [".ppm"],
	mimeType : "image/x-portable-pixmap",
	magic    : ["Portable PixMap bitmap", "Portable Pixel Map", /^Netpbm image data .*pixmap$/]
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
