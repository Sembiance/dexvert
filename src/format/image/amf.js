"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Amiga Metafile Vector Image",
	website        : "http://fileformats.archiveteam.org/wiki/Amiga_Metafile",
	ext            : [".amf"],
	forbidExtMatch : true,
	magic          : ["IFF data, AMFF AmigaMetaFile format"],
	mimeType       : "image/x-amff"
};

exports.converterPriority = ["abydosconvert"];
