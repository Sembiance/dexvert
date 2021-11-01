"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Digi-Pic DGI",
	website : "http://fileformats.archiveteam.org/wiki/DGI_(Digi-Pic)",
	ext     : [".dgi"],
	notes   : "Currently only support converting in black in white. Looks like there may be more color information available?"
};

exports.converterPriority = ["dgiwind"];
