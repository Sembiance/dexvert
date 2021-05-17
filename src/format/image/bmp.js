"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Bitmap Image",
	website  : "http://fileformats.archiveteam.org/wiki/BMP",
	ext      : [".bmp", ".rle", ".dib", ".pic"],
	mimeType : "image/bmp",
	magic    : ["Windows Bitmap", "PC bitmap, Windows 3.x format", "Device independent bitmap graphic"]
};

exports.converterPriorty = ["convert", "graphicWorkshopProfessional", "deark"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
