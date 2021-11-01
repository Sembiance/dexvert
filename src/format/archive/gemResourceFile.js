"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GEM Resource File",
	website : "http://fileformats.archiveteam.org/wiki/GEM_resource_file",
	ext     : [".rsc"],
	notes   : XU.trim`
		deark fails to work with some RSC file such as daleks.rsc and dungeon.rsc
		Better support could be added by coding my own handler by following the format:
		http://cd.textfiles.com/ataricompendium/BOOK/HTML/APPENDC.HTM#rsc`
};

exports.converterPriority = ["deark"];

exports.updateProcessed = (state, p, cb) =>
{
	const r = p.util.program.getRan(state, "deark");
	if(!(r.results || "").trim().toLowerCase().includes("gem rsc, atari"))
		state.processed = false;
	
	setImmediate(cb);
};
