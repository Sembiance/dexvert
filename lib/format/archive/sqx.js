"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Squeez SQX Archive",
	website     : "http://fileformats.archiveteam.org/wiki/SQX",
	ext         : [".sqx"],
	magic       : ["SQX compressed archive"],
	unsupported : true,
	notes       : "Can be extracted by the 'sandbox/app/squeez' program, but this is such a rare format that I haven't bothered adding support for it yet."
};
