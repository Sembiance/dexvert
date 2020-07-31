"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "TheDraw File",
	website     : "http://fileformats.archiveteam.org/wiki/TheDraw_Save_File",
	ext         : [".td"],
	mimeType    : "image/x-thedraw",
	magic       : ["TheDraw design"]
};

exports.converterPriorty = ["abydosconvert"];
