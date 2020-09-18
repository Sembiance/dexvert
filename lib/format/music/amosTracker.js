"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	name    : "AMOS Tracker Bank",
	website : "https://www.exotica.org.uk/wiki/AMOS_file_formats#Regular_memory_bank_format",
	ext     : [".abk"],
	magic   : ["AMOS Memory Bank, Tracker format"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		tiptoe(
			function loadFileData()
			{
				fs.readFile(state.input.absolute, this);
			},
			function extractMod(inputBuffer)
			{
				// Format: https://www.exotica.org.uk/wiki/AMOS_file_formats#Regular_memory_bank_format
				if(inputBuffer.length<22 || inputBuffer.slice(0, 4).toString("utf8")!=="AmBk" || inputBuffer.slice(12, 20).toString("utf8")!=="Tracker ")
					return this.finish();

				// https://www.exotica.org.uk/wiki/Protracker
				this.data.modFilename = `mod.${inputBuffer.slice(20, 40).toString("utf8").replaceAll("\0", "")}`;
				fs.writeFile(path.join(state.cwd, this.data.modFilename), inputBuffer.slice(20), this);
			},
			function performConversion()
			{
				p.util.program.run("xmp", {argsd : [this.data.modFilename]})(state, p, this);
			},
			function getMusicInfo()
			{
				p.util.program.run("modInfo", {argsd : [path.join(state.cwd, this.data.modFilename)]})(state, p, this);
			},
			function stashResults()
			{
				if(state.run.modInfo && state.run.modInfo.length>0 && state.run.modInfo[0] && state.run.modInfo[0].trim().length>0)
				{
					try
					{
						const musicInfo = JSON.parse(state.run.modInfo[0].trim());
						if(Object.keys(musicInfo.length>0))
							state.input.meta.music = musicInfo;
					}
					catch (err) {}
				}

				this();
			},
			cb
		);
	},
	(state, p) => p.util.file.findValidOutputFiles(),
	(state, p) => p.family.validateOutputFiles
];

