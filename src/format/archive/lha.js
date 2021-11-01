"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "LHArc Archive",
	website : "http://fileformats.archiveteam.org/wiki/LHA",
	ext     : [".lha", ".lhz", ".lzs", ".exe"],
	
	// If it's a self-extracting archive, lbrate (and 7z) only work if the extension is .exe. Such silliness.
	safeExt(state) { return (state.identify.map(v => v.magic).some(v => v.startsWith("LHA self-extracting")) ? ".exe" : ".lha"); },
	
	magic   : ["LHARC/LZARK compressed archive", /^LHa .*archive data/, "LHA File Format", "LHA self-extracting", "LHarc self-extracting archive", /^LHarc .*archive data/, "LArc compressed archive"]
};

// Some files are 'LHARK' files that look almost identical to LHA files and can only be identified by trying them as lhark
// Luckilly 'lha' fails on these, so then I try deark with the proper option argument to use the lhark decompression routine
// See: https://entropymine.wordpress.com/2020/12/24/notes-on-lhark-compression-format/
exports.converterPriority = ["lha", {program : "deark", flags : {dearkOpts : ["lha:lhark"]}}, "UniExtract"];
