"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://sidplay2.sourceforge.net/",
	gentooPackage : "media-sound/sidplay",
	flags         :
	{
		sidSubTune    : "Specify which sub tune to convert, zero based. Default: 1",
		sidSongLength : "Duration of time to play the SID song. Default: Let sidplay2 decide"
	}
};

exports.bin = () => "sidplay2";
exports.args = (state, p, r, inPath=state.input.filePath) =>
{
	r.sidPaddedSubTune = `${(r.flags.sidSubTune || 1)}`.padStart(3, "0");
	const sidplayArgs = [`-w${path.join(state.output.dirPath, `outfile_${r.sidPaddedSubTune}.wav`)}`, `-o${r.flags.sidSubTune || 1}`];
	if(r.flags.sidSongLength)
		sidplayArgs.push(`-t${r.flags.sidSongLength}`);
	sidplayArgs.push(inPath);

	return sidplayArgs;
};

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile_${r.sidPaddedSubTune}.wav`), path.join(state.output.absolute, `${state.input.name}_${r.sidPaddedSubTune}.wav`))(state, p, cb);
