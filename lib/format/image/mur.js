"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name     : "C.O.L.R. Object Editor",
	website  : "http://fileformats.archiveteam.org/wiki/C.O.L.R._Object_Editor",
	ext      : [".mur", ".pal"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		const ourExt = state.input.ext.toLowerCase();

		// Both .mur and .pal must be present
		const otherExts = exports.meta.ext.slice().filter(v => v!==ourExt).map(v => (ourExt===state.input.ext ? v : v.toUpperCase()));
		const otherFilePaths = otherExts.map(otherExt => path.join(path.dirname(state.input.absolute), state.input.name + otherExt));
		const hasOtherFilePaths = otherFilePaths.every(otherFilePath => fileUtil.existsSync(otherFilePath));

		if(!hasOtherFilePaths)
		{
			state.processed = false;
			return setImmediate(cb);
		}
		
		if([".pal"].includes(ourExt))
		{
			// We mark the PAL file as processed because only the .mur file can actually be converted
			state.processed = true;
			return setImmediate(cb);
		}

		otherFilePaths.parallelForEach((otherFilePath, subcb) => fs.symlink(otherFilePath, path.join(state.cwd, `in${path.extname(otherFilePath).toLowerCase()}`), subcb), cb);
	},
	() => ({program : "recoil2png"}),
	(state, p) => p.family.validateOutputFiles
];
