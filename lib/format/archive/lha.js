"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "LHArc Archive",
	website : "http://fileformats.archiveteam.org/wiki/LHA",
	ext     : [".lha", ".lhz", ".exe"],
	
	// If it's a self-extracting archive, lbrate (and 7z) only work if the extension is .exe. Such silliness.
	safeExt(state) { return (state.identify.map(v => v.magic).some(v => v.startsWith("LHA self-extracting")) ? ".exe" : ".lha"); },
	
	magic   : ["LHARC/LZARK compressed archive", /^LHa .*archive data/, "LHA File Format", "LHA self-extracting", "LHarc self-extracting archive"]
};

exports.steps = [() => ({program : "lha"})];
