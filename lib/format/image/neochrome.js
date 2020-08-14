"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	image = require(path.join(__dirname, "..", "..", "family", "image.js")),
	fs = require("fs");

exports.meta =
{
	name     : "Neochrome",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome",
	ext      : [".neo", ".rst"],
	mimeType : "image/x-neo",
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if([".rst"].includes(ext))
			return fs.statSync(state.input.absolute).size;

		return 32128;
	}]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		// Only .NEO files can be converted, but IF there is a .rst, it should be symlinked to so color can be included
		const ourExt = state.input.ext.toLowerCase();
		const otherExt = ourExt===".neo" ? (ourExt===state.input.ext ? ".rst" : ".RST") : (ourExt===state.input.ext ? ".neo" : ".NEO");
		const otherFilePath = path.join(path.dirname(state.input.absolute), state.input.name + otherExt);
		const hasOtherFile = fileUtil.existsSync(otherFilePath);
		
		if(ourExt===".rst")
		{
			// We mark the RST file as processed if the required NEO is present, otherwise it's probably not a match for this format
			state.processed = hasOtherFile;
			return setImmediate(cb);
		}

		// If we don't have a .rst file, that's ok, we'll just convert as grayscale
		if(!hasOtherFile)
			return setImmediate(cb);

		fs.symlink(otherFilePath, path.join(state.cwd, `in${otherExt.toLowerCase()}`), cb);
	},
	...image.converterSteps
];

exports.converterPriorty = ["recoil2png", "nconvert", "abydosconvert"];
