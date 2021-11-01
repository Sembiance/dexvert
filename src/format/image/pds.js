"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Planetary Data System",
	website : "http://fileformats.archiveteam.org/wiki/PDS",
	ext     : [".imq", ".img", ".pds"],
	magic   : ["PDS image bitmap", "PDS (JPL) image data"]
};

exports.converterPriority = ["nconvert", "imageAlchemy"];
