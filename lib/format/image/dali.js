"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Dali",
	website  : "http://fileformats.archiveteam.org/wiki/Dali",
	ext      : [".sd0", ".sd1", ".sd2", ".hpk", ".lpk", ".mpk"],
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if([".hpk", ".lpk", ".mpk"].includes(ext))
			return fs.statSync(state.input.absolute).size;

		return 32128;
	}]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
