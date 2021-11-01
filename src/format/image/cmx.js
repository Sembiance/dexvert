"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Corel Metafile Exchange Image",
	website        : "http://fileformats.archiveteam.org/wiki/CMX",
	ext            : [".cmx"],
	forbidExtMatch : true,
	magic          : ["Corel Metafile Exchange Image", "Corel Presentation Exchange File"],
	unsafe         : true
};

exports.converterPriority = [{program : "soffice", flags : {sofficeType : "svg"}}, "deark"];
