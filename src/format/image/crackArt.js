"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Crack Art",
	website  : "http://fileformats.archiveteam.org/wiki/Crack_Art",
	ext      : [".ca1", ".ca2", ".ca3"],
	magic    : ["Crack Art bitmap"]
};

exports.converterPriority = ["recoil2png"];
