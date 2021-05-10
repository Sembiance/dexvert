"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "IFF TDDD 3-D Render Document",
	website     : "http://fileformats.archiveteam.org/wiki/TDDD",
	ext         : [".tdd", ".cel", ".obj"],
	magic       : ["IFF data, TDDD 3-D rendering", "3D Data Description object", "Impulse 3D Data Description Object"],
	unsupported : true,
	notes       : XU.trim`
		A 3D rendering file format. Some of these files may have been created by "Impulse 3D"
		I've never bothered trying to convert or render these into anything else`
};
