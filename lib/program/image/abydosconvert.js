"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://github.com/Sembiance/abydosconvert",
	gentooPackage : "media-gfx/abydosconvert",
	gentooOverlay : "dexvert",
	bruteUnsafe   : true
};

exports.bin = () => "abydosconvert";
exports.args = (state, p, inPath=state.input.filePath, outPath=state.output.dirPath) => ([p.format.meta.mimeType, inPath, outPath]);
exports.runOptions = () => ({timeout : XU.MINUTE*1});	// abydos sometimes just hangs on a conversion eating 100% CPU forever

// abydosconvert can create more than one output file. Some may have a suffix .000 or may not
exports.post = (state, p, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameFiles(outputFilePaths)
		{
			outputFilePaths.parallelForEach((outputFilePath, subcb) =>
			{
				const groups =  (path.basename(outputFilePath).match(/(?<suffix>\.\d{3})?.(?<ext>png|svg|webp)/) || {groups : {}}).groups;
				fs.rename(outputFilePath, path.join(state.output.absolute, `${state.input.name}${groups.suffix || ""}.${groups.ext}`), subcb);
			}, this);
		},
		cb
	);
};
