"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "XLD4 Image",
	website : "http://fileformats.archiveteam.org/wiki/XLD4",
	ext     : [".q4"],
	magic   : ["XLD4 bitmap"]
};

exports.converterPriority = ["recoil2png"];
