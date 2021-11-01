"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ComputerEyes",
	website  : "http://fileformats.archiveteam.org/wiki/ComputerEyes",
	ext      : [".ce1", ".ce2", ".ce3"],
	magic    : ["ComputerEyes Raw Data Format bitmap"]
};

exports.converterPriority = ["recoil2png"];
