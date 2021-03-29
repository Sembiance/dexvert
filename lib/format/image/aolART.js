"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "AOL ART Compressed Image",
	website     : "http://fileformats.archiveteam.org/wiki/ART_(AOL_compressed_image)",
	ext         : [".art"],
	magic       : ["AOL ART image", "AOL ART (Johnson-Grace compressed) bitmap"],
	unsupported : true,
	notes       : "Graphics Workship can convert these files, but it's a crappy bloated commercial program that is unreliable under wine and doesnt offer command line conversion. I hope to find an AOL ART CLI converter in the future."
};
