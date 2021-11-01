"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Rembrandt True Color Picture",
	website : "http://fileformats.archiveteam.org/wiki/Rembrandt",
	ext     : [".tcp"],
	magic   : ["Rembrandt True Color Picture bitmap"]
};

exports.converterPriority = ["recoil2png"];
