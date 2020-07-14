"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	name    : "The Sterling COMPressor archive",
	website : "http://fileformats.archiveteam.org/wiki/TSComp",
	magic   : ["TSComp compressed data", "TSComp archive data"]
};

exports.steps =
[
	() => (state, p, cb) => fs.symlink(path.join(__dirname, "..", "..", "..", "dos", "TSCOMP.EXE"), path.join(state.cwd, "TSCOMP.EXE"), cb),
	(state, p) => p.util.dos.run({autoExec : ["TSCOMP.EXE -l " + state.input.filePath + " > TSFILES.TXT"]}),
	(state, p) =>
	{
		const tscompFilenames = fs.readFileSync(path.join(state.cwd, "TSFILES.TXT"), XU.UTF8).toString("utf8").split("\n").filter(line => line.trim().startsWith("=>")).map(line => line.trim().substring(2));
		return p.util.dos.run({autoExec : tscompFilenames.map(fn => "TSCOMP.EXE -d " + state.input.filePath + " " + state.output.dirPath + "\\" + fn)});
	}
];
