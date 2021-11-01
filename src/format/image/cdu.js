"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "CDU-Paint Image",
	website  : "http://fileformats.archiveteam.org/wiki/CDU-Paint",
	ext      : [".cdu"],
	fileSize : 10277
};

exports.converterPriority = ["recoil2png", "view64"];
