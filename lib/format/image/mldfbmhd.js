"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "MLDF BMHD File",
	ext              : [".mld"],
	magic            : ["MLDF BMHD file"],
	unsupported      : true,
	unsupportedNotes : "It's probably an image format. IFF format FORM with MLDFBMHD. Could not loacate any info online about it. So didn't pursuse further."

};
