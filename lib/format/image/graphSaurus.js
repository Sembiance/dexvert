"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name     : "Graph Saurus",
	website  : "http://fileformats.archiveteam.org/wiki/Graph_Saurus",
	ext      : [".sr5", ".gl5", ".pl5", ".sr6", ".gl6", ".pl6", ".sr7", ".gl7", ".pl7", ".sr8", ".gl8", ".sri", ".srs"],
	magic    : ["Graph Saurus bitmap", "MSX Graph Saurus"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		const ourExt = state.input.ext.toLowerCase();

		// Standalone
		if([".sr8", ".sri"].includes(ourExt))
			return setImmediate(cb);

		// If it is a .sr* or .gl* file, it might also include a .pl* file for additional color info
		const otherExts = (!ourExt.startsWith(".pl") ? (ourExt===state.input.ext ? [".pl"] : [".PL"]) : (ourExt===state.input.ext ? [".sr", ".gl"] : [".SR", ".GL"])).map(ext => ext + ourExt.charAt(3));
		const otherFilePaths = otherExts.map(otherExt => path.join(path.dirname(state.input.absolute), state.input.name + otherExt));
		const hasOtherFilePath = otherFilePaths.find(otherFilePath => fileUtil.existsSync(otherFilePath));
		
		if(ourExt.startsWith(".pl"))
		{
			// We mark the PL* file as processed if the required SR*/GL* is present, otherwise it's probably not a match for this format
			state.processed = !!hasOtherFilePath;
			return setImmediate(cb);
		}

		// If we don't have a .pl* file, that's ok, it'll still convert, it'll just look like ass
		if(!hasOtherFilePath)
			return setImmediate(cb);

		fs.symlink(hasOtherFilePath, path.join(state.cwd, `in${path.extname(hasOtherFilePath).toLowerCase()}`), cb);
	},
	() => ({program : "recoil2png"}),
	(state, p) => p.family.validateOutputFiles
];
