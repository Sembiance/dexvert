"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Roshal Archive",
	website : "http://fileformats.archiveteam.org/wiki/RAR",
	ext     : [".rar"],
	magic   : ["RAR archive data", "RAR compressed archive", "RAR Archive"],
	program : "unrar"
};

exports.post = function post(state, p, cb)
{
	// Check to see if we have an archive comment
	if(state.run.unrar && state.run.unrar.length>0)
	{
		const commentGroups = (state.run.unrar[0].replaceAll("\n", "§").match(/Extracting from in\.rar§(?<comment>.+)§§Extracting/) || {groups : {}}).groups;
		if(commentGroups.comment)
			state.input.meta.rar = {comment : commentGroups.comment.replaceAll("§", "\n").trim()};
	}
		
	setImmediate(cb);
};
