"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name : "Technicolor Dream",
	website : "http://fileformats.archiveteam.org/wiki/Technicolor_Dream",
	ext  : [".lum", ".col"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		// Only .LUM files can be converted, but IF there is a .col, it should be symlinked to so color can be included
		const ourExt = state.input.ext.toLowerCase();
		const otherExt = ourExt===".lum" ? (ourExt===state.input.ext ? ".col" : ".COL") : (ourExt===state.input.ext ? ".lum" : ".LUM");
		const otherFilePath = path.join(path.dirname(state.input.absolute), state.input.name + otherExt);
		const hasOtherFile = fileUtil.existsSync(otherFilePath);
		
		if(ourExt===".col")
		{
			// We mark the COL file as processed if the required LUM is present, otherwise it's probably not a match for this format
			state.processed = hasOtherFile;
			return setImmediate(cb);
		}

		// If we don't have a .col file, that's ok, we'll just convert as grayscale
		if(!hasOtherFile)
			return setImmediate(cb);

		fs.symlink(otherFilePath, path.join(state.cwd, `in${otherExt.toLowerCase()}`), cb);
	},
	() => ({program : "recoil2png"}),
	(state, p) => p.family.validateOutputFiles
];
