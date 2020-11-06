"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Roshal Archive",
	website : "http://fileformats.archiveteam.org/wiki/RAR",
	ext     : [".rar"],
	magic   : ["RAR archive data", "RAR compressed archive", "RAR Archive"]
};

exports.steps = [() => ({program : "unrar"})];

exports.post = (state, p, cb) =>
{
	if(p.util.program.getMeta(state, "unrar"))
		state.input.meta.rar = p.util.program.getMeta(state, "unrar");
		
	setImmediate(cb);
};
