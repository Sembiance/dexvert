"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name      : "Interpaint",
	website   : "http://fileformats.archiveteam.org/wiki/Interpaint",
	ext       : [".iph", ".ipt"],
	magic     : ["Interpaint bitmap"]
};

exports.converterPriorty = ["nconvert", "recoil2png"];
