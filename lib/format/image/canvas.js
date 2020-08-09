"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name : "Atari Canvas",
	ext  : [".cpt", ".hbl", ".ful"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		const ourExt = state.input.ext.toLowerCase();

		// Might just be a standalone format
		if(ourExt===".ful")
			return setImmediate(cb);

		// If it is a .cpt file, it might also include a .hbl file for additional color info
		const otherExt = ourExt===".cpt" ? (ourExt===state.input.ext ? ".hbl" : ".HBL") : (ourExt===state.input.ext ? ".cpt" : ".CPT");
		const otherFilePath = path.join(path.dirname(state.input.absolute), state.input.name + otherExt);
		const hasOtherFile = fileUtil.existsSync(otherFilePath);
		
		if(ourExt===".hbl")
		{
			// We mark the HBL file as processed if the required CPT is present, otherwise it's probably not a match for this format
			state.processed = hasOtherFile;
			return setImmediate(cb);
		}

		// If we don't have a .hbl file, that's ok, we'll just convert as grayscale
		if(!hasOtherFile)
			return setImmediate(cb);

		fs.symlink(otherFilePath, path.join(state.cwd, `in${otherExt}`), cb);
	},
	() => ({program : "recoil2png"}),
	(state, p) => p.family.validateOutputFiles
];
