"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Device Independent File",
	website        : "http://fileformats.archiveteam.org/wiki/DVI_(Device_Independent_File_Format)",
	ext            : [".dvi"],
	forbidExtMatch : true,
	magic          : ["TeX DVI file", "Device Independent Document"],
	notes          : "Once I get more file samples, convert with something better than `strings'. I can try using `dvips` to convert to PS then use ps2pdf. Or use sandbox/app/dvipbm"
};

exports.converterPriorty = ["strings"];
