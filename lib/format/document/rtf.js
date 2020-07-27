"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "WRich Text Format",
	website     : "http://fileformats.archiveteam.org/wiki/RTF",
	ext         : [".rtf"],
	magic       : ["Rich Text Format"],
	bruteUnsafe : true
};

exports.steps = [() => ({program : "unoconv"})];
