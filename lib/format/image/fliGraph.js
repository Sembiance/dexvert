"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "FLI Graph Image",
	website  : "http://fileformats.archiveteam.org/wiki/FLI_GraphF",
	ext      : [".bml", ".fli"],
	filesize : [state => ({".bml" : 17474, ".fli" : 17409}[state.input.ext.toLowerCase()])]
};

exports.converterPriorty = ["recoil2png"];
