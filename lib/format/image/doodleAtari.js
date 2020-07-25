"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Doodle Atari",
	website  : "http://fileformats.archiveteam.org/wiki/Doodle_(Atari)",
	ext      : [".doo"]
};

// All Doodle Atari files are exactly 32,000 bytes in size (a dump of video memory)
exports.custom = state => (fs.statSync(state.input.absolute).size===32000);

exports.converterPriorty = ["deark", "recoil2png"];
