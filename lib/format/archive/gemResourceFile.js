"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GEM Resource File",
	website : "http://fileformats.archiveteam.org/wiki/GEM_resource_file",
	ext     : [".rsc"],
	notes   : "deark fails to work with some RSC file such as daleks.rsc"
};

exports.converterPriorty = ["deark"];

exports.updateProcessed = (state, p, cb) =>
{
	const r = p.util.program.getRan(state, "deark");
	if(!(r.results || "").trim().toLowerCase().includes("gem rsc, atari"))
		state.processed = false;
	
	setImmediate(cb);
};
