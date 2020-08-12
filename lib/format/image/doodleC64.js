"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Doodle C64",
	website  : "http://fileformats.archiveteam.org/wiki/Doodle!_(C64)",
	ext      : [".dd", ".jj"],
	magic    : ["Doodle compressed bitmap"],
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if(ext===".jj")
			return fs.statSync(state.input.absolute).size;

		return [9218, 9026, 9346];
	}]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
