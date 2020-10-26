"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "MLDF File",
	ext         : [".mld"],
	magic       : ["MLDF BMHD file"],
	unsupported : true,
	notes       : "It's probably an image format. IFF format FORM with MLDF BMHD. Could not locate any info online about it and I didn't investigate further."
};
