"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Print Shop Graphic POG Archive Names File",
	website        : "http://fileformats.archiveteam.org/wiki/PrintMaster",
	ext            : [".pnm"],
	filesRequired  : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.pog`)
};

exports.steps = [() => ({program : "strings"})];
