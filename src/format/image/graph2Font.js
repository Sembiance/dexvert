"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Graph2Font",
	website  : "http://g2f.atari8.info",
	ext      : [".g2f", ".mch"],
	magic    : ["Graph2Font bitmap"],
	fileSize : {".mch" : [30833, 32993]}
};

exports.converterPriority = ["recoil2png"];
