"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "HP Printer Command Language",
	website     : "http://fileformats.archiveteam.org/wiki/PCL",
	ext         : [".pcl", ".prn"],
	mimeType    : "application/vnd.hp-PCL",
	magic       : ["HP Printer Command Language", "HP PCL printer data"],
	bruteUnsafe : true
};

exports.steps = [() => ({program : "gpcl6"})];
