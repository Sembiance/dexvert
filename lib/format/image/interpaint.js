"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Interpaint",
	website   : "http://fileformats.archiveteam.org/wiki/Interpaint",
	ext       : [".iph", ".ipt", ".lre", ".hre"],
	magic     : ["Interpaint bitmap"]
};

exports.converterPriorty = ["recoil2png", "nconvert", "view64"];
