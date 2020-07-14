"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "GX2 Bitmap",
	website          : "http://fileformats.archiveteam.org/wiki/GX2",
	ext              : [".gx2"],
	magic            : ["GX2 bitmap"],
	unsupported      : true,
	unsupportedNotes : XU.trim`
		No known converter. File format is detailed though in unsupported/image/gx2/GX2SPEC.DOC
		So in theory I could create my own converter program if I wanted to.`
};
