"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Acorn/RISC-OS Draw",
	website : "http://fileformats.archiveteam.org/wiki/Acorn_Draw",
	magic : ["RISC OS Draw file data", "Acorn Draw vector image"]
};

exports.converterPriority = ["drawview"];
