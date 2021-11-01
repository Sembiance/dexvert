"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "OpenEXR",
	website  : "http://fileformats.archiveteam.org/wiki/OpenEXR",
	ext      : [".exr"],
	mimeType : "image/x-exr",
	magic    : ["OpenEXR High Dynamic-Range bitmap", "OpenEXR image data"]
};

exports.converterPriority = ["abydosconvert"];
