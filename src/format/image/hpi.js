"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Hemera Photo Image",
	website : "http://fileformats.archiveteam.org/wiki/Hemera_Photo-Object",
	ext     : [".hpi"],
	magic   : ["Hemera Photo-Object Image bitmap"],
	notes   : "Kevlar.hpi won't convert for some reason"
};

exports.converterPriority = ["nconvert", "deark"];
