"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "LEADTools Compressed Image",
	website : "http://fileformats.archiveteam.org/wiki/CMP",
	ext     : [".cmp"],
	magic   : ["LEADTools CMP Image Compressed bitmap", "LEADToolsCompressed Image"]
};

exports.converterPriority = ["leadecom"];
