"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name       : "DICOM Bitmap",
	website    : "http://fileformats.archiveteam.org/wiki/DICOM",
	ext        : [".dcm", ".dic"],
	mimeType   : "application/dicom",
	magic      : ["DICOM medical imaging bitmap", "Digital Imaging and Communications in Medicine File Format"]
};

exports.converterPriority = ["abydosconvert"];
