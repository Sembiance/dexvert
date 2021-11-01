"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "ICDRAW Icon",
	website : "http://fileformats.archiveteam.org/wiki/ICDRAW_icon",
	ext     : [".ib3", ".ibi"],
	magic   : ["ICDRAW group icon bitmap", "ICDRAW single icon bitmap"]
};

exports.converterPriority = ["recoil2png"];
