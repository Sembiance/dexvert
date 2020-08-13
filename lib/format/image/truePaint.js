"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "True Paint I",
	website  : "http://fileformats.archiveteam.org/wiki/True_Paint_I",
	ext      : [".mci", ".mcp"],
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if([".mcp"].includes(ext))
			return fs.statSync(state.input.absolute).size;

		return 19434;
	}]
};

exports.converterPriorty = ["recoil2png"];
