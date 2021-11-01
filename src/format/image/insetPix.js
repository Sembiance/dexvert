"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Inset PIX",
	website  : "http://fileformats.archiveteam.org/wiki/Inset_PIX",
	ext      : [".pix"],
	magic    : ["Inset PIX bitmap"]
};

exports.converterPriority = ["deark"];
