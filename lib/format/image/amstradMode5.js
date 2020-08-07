"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name : "Amstrad CPC Mode 5 Image",
	ext  : [".cm5", ".gfx"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		// Both a .cm5 and a .gfx file are required together to form an image
		const ourExt = state.input.ext.toLowerCase();
		const otherExt = ourExt===".gfx" ? (ourExt===state.input.ext ? ".cm5" : ".CM5") : (ourExt===state.input.ext ? ".gfx" : ".GFX");
		const otherFilePath = path.join(path.dirname(state.input.absolute), state.input.name + otherExt);
		state.hasRequiredFiles = fileUtil.existsSync(otherFilePath);
		
		// recoil2png only operates on '.cm5' however and requires <sameName>.gfx to be present in the cwd
		if(ourExt===".gfx")
		{
			// We mark the GFX file as processed if the required CM5 is present, otherwise it's probably not a match for this format
			state.processed = state.hasRequiredFiles;
			return setImmediate(cb);
		}
		
		fs.symlink(otherFilePath, path.join(state.cwd, `in${otherExt}`), cb);
	},
	() => ({program : "recoil2png"}),
	(state, p) => p.family.validateOutputFiles
];
