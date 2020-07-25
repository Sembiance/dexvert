"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/abydosconvert",
	gentooPackage : "media-gfx/abydosconvert",
	gentooOverlay : "dexvert"
};

exports.bin = () => "abydosconvert";
exports.args = (state, p) => ([p.format.meta.mimeType, state.input.filePath, state.output.dirPath]);
exports.runOptions = () => ({timeout : XU.MINUTE*2});	// abydos sometimes just hangs on a conversion eating 100% CPU forever

// It might make more than one output file, all safely named based on temporary safe input filename, so let's rename to our destination name
exports.post = (state, p, cb) =>
{
	[".png", ".svg", ".webp"].map(ext => path.join(state.output.absolute, path.basename(state.input.filePath) + ext)).parallelForEach((intermediateFilePath, subcb) =>
	{
		const intermediateExt = path.extname(intermediateFilePath);
		if(!fileUtil.existsSync(intermediateFilePath))
			return setImmediate(subcb);
		
		if(intermediateExt===".webp")
		{
			// WEBP is only output when it's animated, so let's convert to animated GIF
			p.util.flow.serial([
				subState => ({program : "convert", args : [intermediateFilePath, "-strip", path.join(subState.output.dirPath, `${subState.input.name}.gif`)]}),
				() => p.util.file.unlink(intermediateFilePath)
			])(state, p, subcb);
		}
		else
		{
			// Otherwise, just rename the file to the proper name based on the original input filename
			p.util.file.move(intermediateFilePath, path.join(state.output.absolute, `${state.input.name}${intermediateExt}`))(state, p, subcb);
		}
	}, cb);
};
