"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PCXlib Compressed Archive",
	website : "http://fileformats.archiveteam.org/wiki/PCX_Library",
	ext     : [".pcl"],
	magic   : ["pcxLib compressed", "PCX Library game data container"]
};

exports.converterPriority = ["unpcxgx"];
