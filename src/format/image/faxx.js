"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Facsimile image FORM",
	website     : "http://fileformats.archiveteam.org/wiki/FAXX",
	ext         : [".faxx", ".fax"],
	magic       : ["IFF data, FAXX", "IFF Facsimile image"],
	unsupported : true,
	notes       : "No known converter."
};
