"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ARJ Archive",
	website        : "http://fileformats.archiveteam.org/wiki/ARJ",
	ext            : [".arj", ".exe"],
	forbidExtMatch : [".exe"],
	magic          : ["ARJ compressed archive", "ARJ File Format", "ARJ archive data", "ARJ self-extracting archive"]
};

exports.converterPriority = ["unar", "UniExtract"];
