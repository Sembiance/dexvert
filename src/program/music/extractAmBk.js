"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert",
	unsafe  : true
};

exports.args = (state, p, r, inPath=state.input.absolute) => ([inPath]);
exports.steps = (s0, p0, r) => [
	() => (state, p, cb) =>
	{
		tiptoe(
			function loadFileData()
			{
				fs.readFile(r.args[0], this);
			},
			function extractMod(inputBuffer)
			{
				// Format: https://www.exotica.org.uk/wiki/AMOS_file_formats#Regular_memory_bank_format
				if(inputBuffer.length<22 || inputBuffer.slice(0, 4).toString("utf8")!=="AmBk" || inputBuffer.slice(12, 20).toString("utf8")!=="Tracker ")
					return this.finish();

				// https://www.exotica.org.uk/wiki/Protracker
				// It's important that we add the .mod extension so programs like awaveStudio can convert it properly
				r.modFilePath = path.join(state.cwd, `mod.${inputBuffer.slice(20, 40).toString("utf8").replaceAll("\0", "")}.mod`);
				fs.writeFile(r.modFilePath, inputBuffer.slice(20), this);
			},
			cb
		);
	}
];
