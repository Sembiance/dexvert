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
	if(state.run.meta.unrar)
	{
		state.input.meta.rar = state.run.meta.unrar;
		delete state.run.meta.unrar;
	}
		
	setImmediate(cb);
};
