"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Amiga Metafile Vector Image",
	website        : "http://fileformats.archiveteam.org/wiki/Amiga_Metafile",
	ext            : [".amf"],
	forbidExtMatch : true,
	magic          : ["IFF data, AMFF AmigaMetaFile format"],
	unsupported    : true,
	notes          : "No known modern converter."
};
