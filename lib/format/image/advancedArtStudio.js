"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name     : "Advanced Art Studio",
	website  : "http://fileformats.archiveteam.org/wiki/Advanced_Art_Studio",
	ext      : [".ocp", ".scr", ".win", ".pal"],
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if([".scr", ".win", ".pal"].includes(ext))
			return fs.statSync(state.input.absolute).size;

		return 10018;
	}]
};

exports.custom = state =>
{
	const ourExt = state.input.ext.toLowerCase();
	if(ourExt===".ocp")
		return true;

	// PAL requires either a corresponding .win or .scr
	if(ourExt===".pal")
	{
		const otherExts = exports.meta.ext.slice().removeAll(".ocp").filter(v => v!==ourExt).map(v => (ourExt===state.input.ext ? v : v.toUpperCase()));
		return otherExts.map(otherExt => path.join(path.dirname(state.input.absolute), state.input.name + otherExt)).some(otherFilePath => fileUtil.existsSync(otherFilePath));
	}
	
	// SCR/WIN requires other files
	const otherExts = exports.meta.ext.slice().removeAll(".ocp").filter(v => v!==ourExt).subtractAll([".scr", ".win"]).map(v => (ourExt===state.input.ext ? v : v.toUpperCase()));
	return otherExts.map(otherExt => path.join(path.dirname(state.input.absolute), state.input.name + otherExt)).every(otherFilePath => fileUtil.existsSync(otherFilePath));
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		const ourExt = state.input.ext.toLowerCase();

		// .ocp files are standalone
		if(ourExt===".ocp")
			return setImmediate(cb);

		// A pal file requires either a corresponding .win or .scr
		if(ourExt===".pal")
		{
			const otherExts = exports.meta.ext.slice().removeAll(".ocp").filter(v => v!==ourExt).map(v => (ourExt===state.input.ext ? v : v.toUpperCase()));
			state.processed = otherExts.map(otherExt => path.join(path.dirname(state.input.absolute), state.input.name + otherExt)).some(otherFilePath => fileUtil.existsSync(otherFilePath));
			return setImmediate(cb);
		}

		const otherExts = exports.meta.ext.slice().removeAll(".ocp").filter(v => v!==ourExt).subtractAll([".scr", ".win"]).map(v => (ourExt===state.input.ext ? v : v.toUpperCase()));
		const otherFilePaths = otherExts.map(otherExt => path.join(path.dirname(state.input.absolute), state.input.name + otherExt));
		const hasOtherFilePaths = otherFilePaths.every(otherFilePath => fileUtil.existsSync(otherFilePath));

		if(!hasOtherFilePaths)
		{
			state.processed = false;
			return setImmediate(cb);
		}

		otherFilePaths.parallelForEach((otherFilePath, subcb) => fs.symlink(otherFilePath, path.join(state.cwd, `in${path.extname(otherFilePath).toLowerCase()}`), subcb), cb);
	},
	() => ({program : "recoil2png"}),
	(state, p) => p.family.validateOutputFiles
];
