"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Flickering Flexible Line Interpretation",
	website  : "http://fileformats.archiveteam.org/wiki/FFLI",
	ext      : [".ffli"],
	magic    : ["Flickering Flexible Line Interpratation bitmap"]
};

exports.converterPriority = ["recoil2png"];
