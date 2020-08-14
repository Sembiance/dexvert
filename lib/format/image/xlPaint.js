"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "XL-Paint",
	website : "http://fileformats.archiveteam.org/wiki/XL-Paint",
	ext     : [".xlp", ".max", ".raw"],
	magic   : ["XL-Paint MAX bitmap"]
};

exports.converterPriorty = ["recoil2png"];
