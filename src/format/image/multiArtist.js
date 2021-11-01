"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "multiArtist",
	website  : "http://fileformats.archiveteam.org/wiki/MultiArtist",
	ext      : [".mg1", ".mg2", ".mg4", ".mg8"],
	magic    : ["MultiArtist bitmap", "multiArtist"],
	fileSize : {".mg1" : 19456, ".mg2" : 18688, ".mg4" : [15616, 18688], ".mg8" : 14080}
};

exports.converterPriority = ["recoil2png"];
