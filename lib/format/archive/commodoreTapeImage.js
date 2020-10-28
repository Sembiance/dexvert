"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Commodore Tape Image",
	website : "http://fileformats.archiveteam.org/wiki/T64",
	ext     : [".t64"],
	magic   : ["T64 Tape Image", "Commodore 64 Tape container"]
};

exports.steps = [() => ({program : "DirMaster"})];
