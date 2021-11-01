"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Macintosh Word Document",
	website : "http://fileformats.archiveteam.org/wiki/Microsoft_Word_for_Macintosh",
	magic   : ["Word for the Macintosh document", "Microsoft Word for Macintosh"],
	unsafe  : true
};

exports.converterPriority = ["soffice"];
