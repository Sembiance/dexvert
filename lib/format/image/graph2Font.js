"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Graph2Font",
	website : "http://g2f.atari8.info",
	ext     : [".g2f", ".mch"],
	magic   : ["Graph2Font bitmap"]
};

exports.converterPriorty = ["recoil2png"];
