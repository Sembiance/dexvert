"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Multi-Page PCX",
	website  : "http://fileformats.archiveteam.org/wiki/DCX",
	ext      : [".dcx"],
	mimeType : "image/x-dcx",
	magic    : ["Multipage Zsoft Paintbrush Bitmap Graphics", "DCX multi-page PCX image data", "Graphics Multipage PCX bitmap"]
};

exports.converterPriorty = ["convert", "nconvert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
