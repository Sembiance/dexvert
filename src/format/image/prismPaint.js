"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Prism Paint",
	website  : "http://fileformats.archiveteam.org/wiki/Prism_Paint",
	ext      : [".pnt", ".tpi"],
	mimeType : "image/x-prism-paint",
	magic    : ["Prism Paint bitmap"]
};

exports.converterPriorty = ["abydosconvert", "recoil2png"];
