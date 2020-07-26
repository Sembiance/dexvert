"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "RIFF Multimedia Movie",
	website     : "http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie",
	ext         : [".mmm"],
	magic       : ["MultiMedia Movie format video", /RIFF .*multimedia movie$/],
	unsupported : true,
	notes       : "Couldn't find a converter or player for it"
};
