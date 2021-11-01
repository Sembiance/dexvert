"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SQUASH Archive",
	website : "http://fileformats.archiveteam.org/wiki/Squash_(RISC_OS)",
	magic   : ["squished archive data", "Squash compressed data"],
	notes   : "Alternative de-archiver I didn't try: https://github.com/mjwoodcock/riscosarc/"
};

exports.converterPriority = ["deark"];
