"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Shoot 'Em Up Construction Kit Sprite",
	website  : "http://fileformats.archiveteam.org/wiki/Shoot_%27Em_Up_Construction_Kit",
	ext      : [".a"],
	safeExt  : () => ".a",
	fileSize : 8130
};

exports.converterPriority = ["recoil2png"];
