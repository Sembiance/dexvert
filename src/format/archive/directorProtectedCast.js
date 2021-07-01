"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Macromedia Director Protected Cast",
	website   : "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)",
	ext       : [".cxt"],
	magic     : ["Macromedia Director project"],
	weakMagic : true
};

exports.converterPriorty = ["gameextractor", "swiftyXenaPro"];
