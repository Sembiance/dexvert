"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "PhotoChrome",
	website  : "http://fileformats.archiveteam.org/wiki/PhotoChrome",
	ext      : [".pcs"],
	magic    : ["PhotoChrome bitmap"]
};

exports.converterPriorty = ["recoil2png"];
