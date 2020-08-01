"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Hewlett-Packard Graphics Language",
	website     : "http://fileformats.archiveteam.org/wiki/HPGL",
	ext         : [".hpgl"],
	magic       : ["Hewlett-Packard Graphics Language"],
	unsupported : true,
	notes       : XU.trim`
		Sometimes used for graphics, sometimes used to control plotters and other machines.
		I tried to compile this but it's ancient and failed: http://ftp.funet.fi/index/graphics/packages/hpgl2ps/hpgl2ps.tar.Z
		Quick searches didn't turn up any other 'easy' to grab and use converters, so punt on this for now.`
};
