"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "ZLIB Compressed Data",
	website : "http://fileformats.archiveteam.org/wiki/Zlib",
	magic   : ["zlib compressed data", "ZLIB compressed data"]
};

exports.converterPriority = ["gameextractor", { program : "deark", flags : {dearkModule : "zlib"} }];
