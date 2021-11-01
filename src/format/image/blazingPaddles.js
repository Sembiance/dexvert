"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Blazing Paddles",
	website             : "http://fileformats.archiveteam.org/wiki/Blazing_Paddles",
	ext                 : [".pi"],
	mimeType            : "image/x-blazing-paddles",
	fileSize            : [10240, 10242],
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png", "nconvert", "abydosconvert", "view64"];
