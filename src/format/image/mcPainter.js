"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "McPainter",
	website             : "http://fileformats.archiveteam.org/wiki/McPainter",
	ext                 : [".mcp"],
	fileSize            : 16008,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
