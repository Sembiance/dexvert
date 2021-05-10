"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "Tagged Image File Format",
	website  : "http://fileformats.archiveteam.org/wiki/TIFF",
	ext      : [".tif", ".tiff"],
	mimeType : "image/tiff",
	magic    : ["Tagged Image File Format", "TIFF image data"],
	priority : C.PRIORITY.LOW	// Often other formats are mis-identified as TIFF files such RAW camera files like Sony ARW and kodak*
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
