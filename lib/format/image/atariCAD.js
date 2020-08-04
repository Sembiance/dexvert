"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari CAD",
	website  : "http://fileformats.archiveteam.org/wiki/AtariCAD",
	ext      : [".drg"],
	mimeType : "image/x-atari-cad",
	filesize : [6400]
};

exports.converterPriorty = ["recoil2png", "abydosconvert"];
