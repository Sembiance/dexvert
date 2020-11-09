"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://zakalwe.fi/uade",
	gentooPackage : "app-emulation/uade",
	bruteUnsafe   : true
};

exports.bin = () => "uade123";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) =>
{
	const uadeArgs = ["-e", "wav", "-f", outPath, inPath];
	if(r.flags.uadeType)
		uadeArgs.unshift("-P", `/usr/share/uade2/players/${r.flags.uadeType}`);
	
	return uadeArgs;
};
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
