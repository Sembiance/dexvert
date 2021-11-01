"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "IFF RGBN Image",
	website  : "http://fileformats.archiveteam.org/wiki/ILBM",
	ext      : [".iff", ".rgbn"],
	magic    : [/^IFF data, RGB.* image$/, /$IFF .* RGB bitmap$/]
};

exports.converterPriority = ["recoil2png"];
