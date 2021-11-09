/*
import {Program} from "../../Program.js";

export class bchunk extends Program
{
	website = "http://he.fi/bchunk/";
	gentooPackage = "app-cdr/bchunk";
	unsafe = true;
	flags = {"bchunkSwapByteOrder":"If set to true, will swap the byte ordering for WAVs extracted from audio tracks with bchunk"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website       : "http://he.fi/bchunk/",
	gentooPackage : "app-cdr/bchunk",
	unsafe        : true,
	flags         :
	{
		bchunkSwapByteOrder : "If set to true, will swap the byte ordering for WAVs extracted from audio tracks with bchunk"
	}
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
	// Some programs (cdrdao) by default will rip audio tracks from CDs in the big-endian byte order, which is not the standard and produces static output WAVs when bchunk tries to convert them
	// I haven't figured out a way to 'detect' these bad rips, so the best I can do is provide a flag to tell bchunk to swap the byte order for the audio tracks, which will produce the proper WAV files
	const bchunkArgs = ["-w"];
	if(r.flags.bchunkSwapByteOrder)
		bchunkArgs.push("-s");
	
	return [...bchunkArgs, path.relative(r.bchunkWipPath, path.join(state.cwd, inPath)), path.relative(r.bchunkWipPath, cueFilePath), `${state.input.name}-`];
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
*/
