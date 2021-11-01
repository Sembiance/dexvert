"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "DeskPic",
	website : "http://fileformats.archiveteam.org/wiki/DeskPic",
	ext     : [".gfb"],
	magic   : ["DeskPic bitmap"]
};

exports.converterPriority = ["recoil2png"];
