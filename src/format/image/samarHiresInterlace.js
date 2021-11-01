"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "SAMAR Hires Interlace",
	website             : "http://fileformats.archiveteam.org/wiki/SAMAR_Hires_Interlace",
	ext                 : [".shc"],
	fileSize            : 17920,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
