"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Atari CAD",
	website             : "http://fileformats.archiveteam.org/wiki/AtariCAD",
	ext                 : [".drg"],
	mimeType            : "image/x-atari-cad",
	fileSize            : 6400,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png", "abydosconvert"];
