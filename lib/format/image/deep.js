"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "IFF-DEEP",
	website : "http://fileformats.archiveteam.org/wiki/IFF-DEEP",
	ext     : [".deep"],
	magic   : ["IFF DEEP animation/bitmap", "IFF data, DEEP"]
};

exports.converterPriorty = ["recoil2png", "ffmpeg"];
