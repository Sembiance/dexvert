"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "multiArtist",
	website  : "http://fileformats.archiveteam.org/wiki/MultiArtist",
	ext      : [".mg1", ".mg2", ".mg4", ".mg8"],
	magic    : ["MultiArtist bitmap", "multiArtist"],
	filesize : [19456, 18688, 15616, 14080]
};

exports.converterPriorty = ["recoil2png"];
