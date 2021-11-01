"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "TTComp Archive",
	website : "http://fileformats.archiveteam.org/wiki/TTComp_archive",
	magic   : ["TTComp archive"]
};

exports.converterPriority = ["ttdecomp"];
