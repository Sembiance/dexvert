"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website        : ["http://timidity.sourceforge.net/", "http://freepats.opensrc.org", "http://musescore.org/en/handbook/soundfont", "http://www.stardate.bc.ca/eawpatches/html/default.htm"],
	gentooPackage  : ["media-sound/timidity++", "media-sound/timidity-freepats", "media-sound/fluid-soundfont", "media-sound/timidity-eawpatches"],
	bin            : ["timidity", "*", "*"],
	gentooUseFlags : "X alsa flac gtk ncurses speex vorbis",
	bruteUnsafe    : true
};

exports.bin = () => "timidity";

const INSTRUMENT_NAMES = ["eaw", "fluid", "roland", "creative", "freepats", "windows"];	// Ordered by best sounding
const INSTRUMENT_DIR_PATH = path.resolve(path.join(__dirname, "..", "..", "..", "music", "midiInstrument"));

exports.pre = (state, p, cb) =>
{
	if(!state.midiInstrument)
		state.midiInstrument = INSTRUMENT_NAMES[0];

	fs.symlink(path.join(INSTRUMENT_DIR_PATH, state.midiInstrument), path.join(state.cwd, "current"), cb);
};
exports.args = (state, p, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["-Ow", "-o", outPath, inPath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
