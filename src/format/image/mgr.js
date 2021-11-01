"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Manager Windowing System Bitmap",
	website : "http://fileformats.archiveteam.org/wiki/MGR_bitmap",
	ext     : [".mgr"],
	magic   : ["MGR bitmap"]
};

exports.converterPriority = ["nconvert"];
