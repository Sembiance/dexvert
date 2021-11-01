"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Texinfo Document",
	ext   : [".texinfo", ".texi"],
	magic : ["TeX document"]
};

exports.converterPriority = ["texi2html", "texi2pdf", "strings"];
