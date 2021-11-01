"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MAN Page",
	website        : "http://fileformats.archiveteam.org/wiki/Man_page",
	ext            : [".man", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8"],
	forbidExtMatch : true,
	magic          : ["Man page", "troff or preprocessor input"]
};

exports.converterPriority = ["man2html"];
