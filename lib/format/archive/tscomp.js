"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	{DOS} = require("@sembiance/xutil").dos;

exports.meta =
{
	name    : "The Sterling COMPressor archive",
	website : "http://fileformats.archiveteam.org/wiki/TSComp",
	magic   : ["TSComp compressed data", "TSComp archive data"],
	program : "unar"
};

exports.steps = () => ([(state, p, cb) =>
{
	tiptoe(
		function symlinkProgram()
		{
			fs.symlink(path.join(__dirname, "..", "..", "..", "dos", "TSCOMP.EXE"), path.join(state.cwd, "TSCOMP.EXE"), this);
		},
		function generateFileList()
		{
			DOS.quickOp({
				dosCWD     : state.cwd,
				autoExec   : ["TSCOMP.EXE -l " + state.input.filePath + " > TSFILES.TXT"],
				timeout    : XU.MINUTE*3,
				tmpDirPath : state.tmpDirPath}, this);
		},
		function extractFiles()
		{
			const tscompFilenames = fs.readFileSync(path.join(state.cwd, "TSFILES.TXT"), XU.UTF8).toString("utf8").split("\n").filter(line => line.trim().startsWith("=>")).map(line => line.trim().substring(2));
			
			DOS.quickOp({
				dosCWD     : state.cwd,
				timeout    : XU.MINUTE*3,
				tmpDirPath : state.tmpDirPath,
				autoExec   : tscompFilenames.map(fn => "TSCOMP.EXE -d " + state.input.filePath + " " + state.output.dirPath + "\\" + fn)}, this);
		},
		cb
	);
}]);

