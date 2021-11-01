"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Speccy eXtended Graphic",
	ext   : [".sxg"],
	magic : ["Speccy eXtended Graphics bitmap"]
};

exports.converterPriority = ["recoil2png"];
