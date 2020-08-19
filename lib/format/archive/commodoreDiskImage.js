"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	fs = require("fs");

exports.meta =
{
	name    : "Commodore Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/D64",
	ext     : [".d64", ".d81", ".d71", ".g64"],
	magic   : ["D64 Image", "D81 Image", "G64 GCR-encoded Disk Image Format", "G64 1541 raw disk image"]
};

exports.steps =
[
	() => (state, p, cb) => fs.symlink(state.input.absolute, path.join(state.output.absolute, `in${state.input.ext}`), cb),
	(state, p) => p.util.wine.run({cmd : "DirMaster/DirMaster.exe", args : ["--exportall", `in${state.input.ext}`], cwd : state.output.absolute}),
	() => (state, p, cb) =>
	{
		// DirMaster adds .prg extension to pretty much every file, which is kinda excessive. Let's strip it out so we can match against the real extensions
		tiptoe(
			function findPRGOutputFiles()
			{
				fileUtil.glob(state.output.absolute, "*.prg", this);
			},
			function stripPRGExtension(prgFilePaths)
			{
				prgFilePaths.parallelForEach((prgFilePath, subcb) => fs.rename(prgFilePath, prgFilePath.substring(0, prgFilePath.length-(".prg".length)), subcb), this);
			},
			cb
		);
	}
];
