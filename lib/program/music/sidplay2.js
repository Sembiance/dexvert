"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://sidplay2.sourceforge.net/",
	gentooPackage : "media-sound/sidplay"
};

exports.bin = () => "sidplay2";
exports.args = (state, p, r, inPath=state.input.filePath) =>
{
	state.sidPaddedSubTune = `${(state.sidSubTune || 1)}`.padStart(3, "0");
	const sidplayArgs = [`-w${path.join(state.output.dirPath, `outfile_${state.sidPaddedSubTune}.wav`)}`, `-o${state.sidSubTune || 1}`];
	if(state.sidSongLength)
		sidplayArgs.push(`-t${state.sidSongLength}`);
	sidplayArgs.push(inPath);

	return sidplayArgs;
};

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile_${state.sidPaddedSubTune}.wav`), path.join(state.output.absolute, `${state.input.name}_${state.sidPaddedSubTune}.wav`))(state, p, cb);
