"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	path = require("path");

exports.meta =
{
	name    : "Commodore SID Music File",
	website : "http://fileformats.archiveteam.org/wiki/SID",
	ext     : [".sid", ".psid", ".mus"],
	magic   : ["Play SID Audio", "PlaySID", "SID tune"]
};

const SONGLENGTHS_FILE_PATH = path.join(__dirname, "..", "..", "..", "music", "sid", "Songlengths.txt");

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function getSIDInfo()
		{
			runUtil.run("sidplay2", ["-w/dev/null", "-t1", state.input.filePath], Object.assign(p.util.program.runOptions(state), {timeout : XU.MINUTE*5}), this.parallel());
			fs.readFile(SONGLENGTHS_FILE_PATH, XU.UTF8, this.parallel());
		},
		function stashSIDInfo(sidInfo, songLengthsRaw)
		{
			state.input.meta.sid = {subSongCount : +(sidInfo.match(/Playlist.*\(tune \d+\/(?<subSongCount>\d+)/) || {groups : {}}).groups.subSongCount };

			const songLengths = [];

			let nextLine=false;
			songLengthsRaw.trim().split(songLengthsRaw.includes("\n") ? "\n" : "\r").forEach(line =>
			{
				if(nextLine)
				{
					songLengths.push(...line.split("=")[1].trim().split(" "));
					nextLine = false;
				}
				else if(line.startsWith(";") && line.trim().toLowerCase().endsWith(state.input.base.toLowerCase()))
				{
					nextLine = true;
				}
			});

			if(songLengths.length>0)
				state.input.meta.sid.songLengths = songLengths;

			this();
		},
		cb
	);
};

exports.steps =
[
	(state0, p0) => p0.util.flow.parallel([].pushSequence(1, (state0.input.meta.sid.subSongCount || 1)).map(sidSubTune => state => ({program : "sidplay2", flags : {sidSubTune, sidSongLength : (state.input.meta.sid.songLengths || [])[(sidSubTune)-1] || "3:0"}}))),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];
