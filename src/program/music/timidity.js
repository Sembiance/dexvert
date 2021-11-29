/*
import {Program} from "../../Program.js";

export class timidity extends Program
{
	website = ["http://timidity.sourceforge.net/","http://freepats.opensrc.org","http://musescore.org/en/handbook/soundfont","http://www.stardate.bc.ca/eawpatches/html/default.htm"];
	gentooPackage = ["media-sound/timidity++","media-sound/timidity-freepats","media-sound/fluid-soundfont","media-sound/timidity-eawpatches"];
	bin = ["timidity","*","*"];
	gentooUseFlags = "X alsa flac gtk ncurses speex vorbis";
	unsafe = true;
	flags = {"midiFont":"Which midifont to use to convert (eaw, fluid, roland, creative, freepats, windows) Default: eaw"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	path = require("path");

const INSTRUMENT_NAMES = ["eaw", "fluid", "roland", "creative", "freepats", "windows"];	// Ordered by best sounding
const INSTRUMENT_DIR_PATH = path.resolve(path.join(__dirname, "..", "..", "..", "music", "midiFont"));

exports.meta =
{
	website        : ["http://timidity.sourceforge.net/", "http://freepats.opensrc.org", "http://musescore.org/en/handbook/soundfont", "http://www.stardate.bc.ca/eawpatches/html/default.htm"],
	gentooPackage  : ["media-sound/timidity++", "media-sound/timidity-freepats", "media-sound/fluid-soundfont", "media-sound/timidity-eawpatches"],
	bin            : ["timidity", "*", "*"],
	gentooUseFlags : "X alsa flac gtk ncurses speex vorbis",
	unsafe         : true,
	flags          :
	{
		midiFont : `Which midifont to use to convert (${INSTRUMENT_NAMES.join(", ")}) Default: ${INSTRUMENT_NAMES[0]}`
	}
};

exports.bin = () => "timidity";

// Some MIDI files are buggy and have 2 hour+ run times, others seem to loop for hours. So specify a sane timeout, it'll then handle the WAV that it did produce, which will be good enough
exports.runOptions = () => ({timeout : XU.MINUTE*3});

exports.preArgs = (state, p, r, cb) =>	// ROB DENO: preArgs stuff can now just be done inside of args itself, since it's async now
{
	if(!r.flags.midiFont)
		r.flags.midiFont = INSTRUMENT_NAMES[0];

	r.instrumentDirPath = INSTRUMENT_NAMES.includes(r.flags.midiFont) ? path.join(INSTRUMENT_DIR_PATH, r.flags.midiFont) : fileUtil.generateTempFilePath();
	if(INSTRUMENT_NAMES.includes(r.flags.midiFont))
		return setImmediate(cb);

	// If we didn't have that instrument name, assume we've been passed a file path to a specific sound font to use instead
	tiptoe(
		function createMidiFontDir()
		{
			fs.mkdir(r.instrumentDirPath, {recursive : true}, this);
		},
		function symlinkSoundFond()
		{
			fs.symlink(r.flags.midiFont, path.join(r.instrumentDirPath, path.basename(r.flags.midiFont)), this.parallel());
			fs.writeFile(path.join(r.instrumentDirPath, "timidity.cfg"), `dir ${r.instrumentDirPath}\nsoundfont "${path.basename(r.flags.midiFont)}" order=0`, XU.UTF8, this.parallel());
		},
		cb
	);
};
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["-c", path.join(r.instrumentDirPath, "timidity.cfg"), "-Ow", "-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.flow.parallel([
	() => (INSTRUMENT_NAMES.includes(r.flags.midiFont) ? p.util.flow.noop : p.util.file.unlink(r.instrumentDirPath)),
	() => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))
])(state, p, cb);
*/
