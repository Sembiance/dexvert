"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AFLI-Editor Image",
	website  : "http://fileformats.archiveteam.org/wiki/AFLI-Editor",
	ext      : [".afl"]
};

exports.converterPriorty = ["recoil2png", "view64"];
