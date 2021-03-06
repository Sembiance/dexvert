"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "GEM Vector Metafile",
	website     : "http://fileformats.archiveteam.org/wiki/GEM_VDI_Metafile",
	ext         : [".gem", ".gdi"],
	magic       : [/^GEM [Mm]etafile/],
	unsupported : true,
	notes       : "Vector file format that could be converted into SVG. abydos is working on adding support for this format."
};

exports.converterPriorty = ["recoil2png"];
