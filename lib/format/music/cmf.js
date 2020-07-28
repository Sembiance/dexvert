"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Creative Music Format",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".cmf"],
	magic   : ["Creative Music Format", "Creative Music (CMF) data"]
};

exports.converterPriorty = ["adplay"];
