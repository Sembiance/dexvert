"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari ICE* Image",
	website  : "http://fileformats.archiveteam.org/wiki/ICE*",
	ext      : [".icn", ".imn", ".ipc", ".ip2"]
};

exports.converterPriorty = ["recoil2png"];
