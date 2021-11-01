"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Taquart Interlace Picture",
	website : "http://fileformats.archiveteam.org/wiki/Taquart_Interlace_Picture",
	ext     : [".tip"],
	magic   : ["Taquart Interlace Picture bitmap"]
};

exports.converterPriority = ["recoil2png"];
