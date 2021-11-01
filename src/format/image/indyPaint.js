"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "IndyPaint",
	website : "http://fileformats.archiveteam.org/wiki/IndyPaint",
	ext     : [".tru"],
	magic   : ["IndyPaint bitmap"]
};

exports.converterPriority = ["recoil2png"];
