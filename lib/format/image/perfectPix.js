"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name     : "Perfect Pix",
	website  : "http://fileformats.archiveteam.org/wiki/Perfect_Pix",
	ext      : [".eve", ".odd", ".pph"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		const ourExt = state.input.ext.toLowerCase();

		// All three .eve, .odd and .pph must be present
		const otherExts = exports.meta.ext.slice().filter(v => v!==ourExt).map(v => (ourExt===state.input.ext ? v : v.toUpperCase()));
		const otherFilePaths = otherExts.map(otherExt => path.join(path.dirname(state.input.absolute), state.input.name + otherExt));
		const hasOtherFilePaths = otherFilePaths.every(otherFilePath => fileUtil.existsSync(otherFilePath));

		if(!hasOtherFilePaths)
		{
			state.processed = false;
			return setImmediate(cb);
		}
		
		if([".eve", ".odd"].includes(ourExt))
		{
			// We mark the EVE/ODD files as processed because only the .pph file can actually be converted
			state.processed = true;
			return setImmediate(cb);
		}

		otherFilePaths.parallelForEach((otherFilePath, subcb) => fs.symlink(otherFilePath, path.join(state.cwd, `in${path.extname(otherFilePath).toLowerCase()}`), subcb), cb);
	},
	() => ({program : "recoil2png"}),
	(state, p) => p.family.validateOutputFiles
];
