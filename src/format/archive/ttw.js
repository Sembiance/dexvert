"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "TTW Compressed File",
	website : "http://fileformats.archiveteam.org/wiki/TTW",
	ext     : [".cr"],
	magic   : ["TTW Compressed File"]
};

exports.converterPriority = ["xfdDecrunch"];
