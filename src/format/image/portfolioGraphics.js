"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Portfolio Graphics",
	website             : "http://fileformats.archiveteam.org/wiki/PGF_(Portfolio_Graphics)",
	ext                 : [".pgf"],
	fileSize            : 1920,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
