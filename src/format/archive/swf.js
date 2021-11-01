"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Macromedia Flash",
	website        : "http://fileformats.archiveteam.org/wiki/SWF",
	ext            : [".swf"],
	forbidExtMatch : true,
	magic          : ["Macromedia Flash data", "Macromedia Flash Player Movie"]
};

exports.converterPriority = ["ffdec", "swfextract", "ffmpeg"];
