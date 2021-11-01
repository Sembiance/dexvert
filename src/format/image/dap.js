"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "SlideShow for VBXE",
	website  : "http://fileformats.archiveteam.org/wiki/SlideShow_for_VBXE",
	ext      : [".dap"],
	fileSize : 77568
};

exports.converterPriority = ["recoil2png", "nconvert"];
