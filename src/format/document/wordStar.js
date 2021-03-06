"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "WordStar Document",
	website  : "http://fileformats.archiveteam.org/wiki/Wordstar",
	ext      : [".ws", ".ws3", ".ws5", ".ws7", ".ws2", ".wsd"],
	magic    : [/^WordStar .*document$/, "WordStar document"]
};

exports.converterPriorty = ["wordStar"];
