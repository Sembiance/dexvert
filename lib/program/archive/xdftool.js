"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://lallafa.de/blog/amiga-projects/amitools/",
	gentooPackage : "app-arch/amitools",
	gentooOverlay : "dexvert"
};

exports.bin = () => "xdftool";

/*exports.pre = (state, p, cb) =>
{
	tiptoe(
		function getFileDates()
		{
			runUtil.run("xdftool", [state])
		}
	);
	state.helpdecoTmpDirPath = fileUtil.generateTempFilePath(state.tmpDir);
	fs.mkdir(state.helpdecoTmpDirPath, {recursive : true}, cb);
};*/

exports.args = (state, p, inPath=state.input.filePath, outPath=state.output.dirPath) => ([inPath, "unpack", outPath]);
