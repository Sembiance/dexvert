"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GFA-BASIC Atari",
	website : "http://fileformats.archiveteam.org/wiki/Atari_BASIC_tokenized_file",
	ext     : [".gfa", ".bas"],
	magic   : ["GFA-BASIC Atari", "GFA-BASIC 3 data"],
	notes   : "The gfalist program only supports decompiling tokenized files of version 3 and higher."
};

exports.converterPriority = ["gfalist"];
