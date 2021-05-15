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

exports.converterPriorty = state =>
{
	const converters = [];

	// Some TIFF files, especial older ones, have invalid properties (hi100.tiff) that causes imagemagick to produce a 'transparent' image, even though there is data in the image. Weird.
	// We check to see if it was correctly identified as a TIFF (from supportedInputMeta) and if not correct we convert without the alpha channel which seems to fix them
	if(state.input?.meta?.image?.format==="TIFF")
		converters.push("convert");
	else
		converters.push({program : "convert", flags : {removeAlpha : true}});

	converters.push("deark", "imageAlchemy", "graphicsWorkshopProfessional");
	return converters;
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
