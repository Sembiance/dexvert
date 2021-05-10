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
	unsafe   : true
};

exports.bin = () => "abydosconvert";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["--json", p.format.meta.mimeType, inPath, outPath]);
exports.runOptions = () => ({timeout : XU.MINUTE*1, "ignore-stderr" : true});	// Timeout is because abydos sometimes just hangs on a conversion eating 100% CPU forever. ignore-stderr is due to wanting a clean parse of the resulting JSON

// abydosconvert can create more than one output file. Some may have a suffix .000 or may not
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameFiles(outputFilePaths)
		{
			// abydos has the nasty habit of producing 'empty' SVG files that are 0x0 when fed files that are not valid (such as image/sunRaster/OPENING.SCR which is interpreted as an image/aniST file)
			// Sadly ImageMagick identifies this as having a width/height of 300x150 for whatever stupid reason, probably some stupid built in default
			// So let's check the resulting JSON from abydos and if height & width are both zero and we only have .svg files as output, delete our output files
			const abydosResult = XU.parseJSON(r.results, {});
			if(abydosResult.width===0 && abydosResult.height===0 && !outputFilePaths.some(outputFilePath => !outputFilePath.toLowerCase().endsWith(".svg")))
				return outputFilePaths.parallelForEach((outputFilePath, subcb) => fileUtil.unlink(outputFilePath, subcb), this);

			outputFilePaths.parallelForEach((outputFilePath, subcb) =>
			{
				const groups =  (path.basename(outputFilePath).match(/(?<suffix>\.\d{3})?.(?<ext>png|svg|webp)$/) || {groups : {}}).groups;
				fs.rename(outputFilePath, path.join(state.output.absolute, `${state.input.name}${groups.suffix || ""}.${groups.ext}`), subcb);
			}, this);
		},
		cb
	);
};
