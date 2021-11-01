"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Commodore Tape Image",
	website : "http://fileformats.archiveteam.org/wiki/T64",
	ext     : [".t64"],
	magic   : ["T64 Tape Image", "Commodore 64 Tape container"]
};

// Alternatively we can use c1541 to convert the tape image to a d64 image and then process it through c1541. See: https://immerhax.com/?p=136
exports.converterPriority = ["DirMaster"];
