"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "PrintMaster Shape Names",
	website        : "http://fileformats.archiveteam.org/wiki/PrintMaster",
	ext            : [".sdr"],
	filesRequired  : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.shp`)
};

exports.steps = [() => ({program : "strings"})];
