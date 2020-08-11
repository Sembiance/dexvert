"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "multiArtist",
	website : "http://multiartist.untergrund.net/",
	ext     : [".mg1", ".mg2", ".mg4", ".mg8"],
	magic   : ["MultiArtist bitmap", "multiArtist"]
};

exports.converterPriorty = ["recoil2png"];
