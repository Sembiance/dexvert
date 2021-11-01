"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "ARQ Archive",
	website : "http://fileformats.archiveteam.org/wiki/ARQ",
	ext     : [".arq"],
	magic   : ["ARQ archive"]
};

exports.converterPriority = ["arq"];
