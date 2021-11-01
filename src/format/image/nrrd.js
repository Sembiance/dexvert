"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Nearly Raw Raster Data",
	website  : "http://teem.sourceforge.net/nrrd/format.html",
	ext      : [".nrrd"],
	magic    : ["Nearly Raw Raster Data"],
	mimeType : "image/x-nrrd"
};

exports.converterPriority = ["abydosconvert"];
