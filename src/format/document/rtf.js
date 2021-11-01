"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Rich Text Format",
	website        : "http://fileformats.archiveteam.org/wiki/RTF",
	ext            : [".rtf"],
	forbidExtMatch : true,
	magic          : ["Rich Text Format"],
	unsafe         : true
};

exports.converterPriority = ["fileMerlin", "soffice"];
