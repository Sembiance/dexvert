"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "IFF YAFA Animation",
	website     : "http://fileformats.archiveteam.org/wiki/YAFA",
	ext         : [".yafa"],
	magic       : ["IFF data, YAFA animation", "YAFA Animation"],
	unsupported : true,
	notes       : XU.trim`
		No modern converter/player exists.
		Full file format details here: https://aminet.net/package/docs/misc/YAFA-doc
		Amiga converter here: https://aminet.net/package/gfx/misc/YAFA
		Dead 404 converter here: http://eab.abime.net/showthread.php?t=85340`
};
