"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "The Sterling COMPressor archive",
	website : "http://fileformats.archiveteam.org/wiki/TSComp",
	magic   : ["zTSComp compressed data", "zTSComp archive data"],
	program : "unar",
	unsupported : true
};

/*
	{DOS} = require("./dosUtil.js"),
function tscompExtract(filePath, extractionPath, cb)
{
	const tsFilesTmpFilePath = fileUtil.generateTempFilePath("/mnt/ram/tmp", ".txt");

	tiptoe(
		function generateFileList()
		{
			DOS.quickOp({
				inFiles  : {[filePath] : "TMP/F.TSC"},
				outFiles : {"TMP/TSFILES.TXT" : tsFilesTmpFilePath},
				timeout  : XU.MINUTE,
				cmds     : ["C:\\APP\\TSCOMP.EXE -l C:\\TMP\\F.TSC > C:\\TMP\\TSFILES.TXT"]}, this);
		},
		function extractFiles()
		{
			const tscompFilenames = fs.readFileSync(tsFilesTmpFilePath, XU.UTF8).toString("utf8").split("\n").filter(line => line.trim().startsWith("=>")).map(line => line.trim().substring(2));
			const outFiles = {};
			tscompFilenames.forEach(tscompFilename => { outFiles[path.join("TMP", tscompFilename)] = path.join(extractionPath, tscompFilename); });
			
			DOS.quickOp({
				inFiles  : {[filePath] : "TMP/F.TSC"},
				outFiles,
				timeout  : XU.MINUTE,
				cmds     : ["cd TMP", ...tscompFilenames.map(fn => "C:\\APP\\TSCOMP.EXE -d F.TSC " + fn)]}, this);
		},
		function cleanup()
		{
			fileUtil.unlink(tsFilesTmpFilePath, this);
		},
		cb
	);
}
*/
