"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/abydosconvert",
	gentooPackage : "media-gfx/abydosconvert",
	gentooOverlay : "dexvert",
	bruteUnsafe   : true
};

exports.bin = () => "abydosconvert";
exports.args = (state, p) => ([p.format.meta.mimeType, state.input.filePath, state.output.dirPath]);
exports.runOptions = () => ({timeout : XU.MINUTE*2});	// abydos sometimes just hangs on a conversion eating 100% CPU forever

// It might make more than one output file, all safely named based on temporary safe input filename, so let's rename to our destination name
exports.post = (state0, p0, cb) => p0.util.flow.parallel([
	(state, p) => p.util.file.move(path.join(state.output.absolute, `${path.basename(state.input.filePath)}.png`), path.join(state.output.absolute, `${state.input.name}.png`)),
	(state, p) => p.util.file.move(path.join(state.output.absolute, `${path.basename(state.input.filePath)}.webp`), path.join(state.output.absolute, `${state.input.name}.webp`)),
	(state, p) => p.util.file.move(path.join(state.output.absolute, `${path.basename(state.input.filePath)}.svg`), path.join(state.output.absolute, `${state.input.name}.svg`))
])(state0, p0, cb);
