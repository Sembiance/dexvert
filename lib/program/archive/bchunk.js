"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website        : "http://he.fi/bchunk/",
	gentooPackage  : "app-cdr/bchunk",
	bruteUnsafe    : true
};

exports.bin = () => "bchunk";

exports.preArgs = (state, p, r, cb) =>
{
	r.bchunkWipPath = fileUtil.generateTempFilePath(state.cwd, "-bchunk");
	fs.mkdir(r.bchunkWipPath, {recursive : true}, cb);
};

exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.absolute, cueFilePath) =>
{
	r.bchunkOutPath = outPath;
	return ["-w", path.relative(r.bchunkWipPath, path.join(state.cwd, inPath)), path.relative(r.bchunkWipPath, cueFilePath), `${state.input.name}-`];
};

exports.runOptions = (state, p, r) => ({cwd : r.bchunkWipPath});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputFiles()
		{
			fileUtil.glob(r.bchunkWipPath, "**", this);
		},
		function convertOutputFiles(outputFilePaths)
		{
			// Convert with dexvert any resulting files from bchunk. This includes .iso and .wav files
			outputFilePaths.parallelForEach((outputFilePath, subcb) => p.util.program.run("dexvert", {argsd : [outputFilePath, r.bchunkOutPath]})(state, p, subcb), this);
		},
		function removeWipDir()
		{
			if(state.verbose>=5)
				this();
			else
				fileUtil.unlink(r.bchunkWipPath, this);
		},
		cb
	);
};
