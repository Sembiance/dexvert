/*
import {Format} from "../../Format.js";

export class smus extends Format
{
	name = "Simple Musical Score";
	website = "http://fileformats.archiveteam.org/wiki/Amiga_Module";
	ext = [".smus",".song"];
	magic = ["SMUS IFF Simple Musical Score","IFF data, SMUS simple music"];
	notes = "\nThe 'SMUS' format was used by many different programs including Sonix and Deluxe Music.\nThis first tries to convert SONIX SMUS with instrument support using uade123.\nThat cna fail though, then falls back to SMUS2MIDI and SMUSMIDI, losing instrument samples.\nSMUS2MIDI seems to work on more files, but it gets several of them a bit wrong (Rhapsody.smus)\nSMUSMIDI is pretty good, but it crashes on many files, requiring a full timeout wait of the rexx script.";
	converters = [{"program":"uade123"},["smus2midi",{"program":"dexvert","flags":{"asFormat":"music/mid","deleteInput":true}}],["smusmidi",{"program":"dexvert","flags":{"asFormat":"music/mid","deleteInput":true}}]]

preSteps = [null];

postSteps = [null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name    : "Simple Musical Score",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".smus", ".song"],
	magic   : ["SMUS IFF Simple Musical Score", "IFF data, SMUS simple music"],
	notes   : XU.trim`
		The 'SMUS' format was used by many different programs including Sonix and Deluxe Music.
		This first tries to convert SONIX SMUS with instrument support using uade123.
		That cna fail though, then falls back to SMUS2MIDI and SMUSMIDI, losing instrument samples.
		SMUS2MIDI seems to work on more files, but it gets several of them a bit wrong (Rhapsody.smus)
		SMUSMIDI is pretty good, but it crashes on many files, requiring a full timeout wait of the rexx script.`
};

const INSTRUMENT_DIR_PATH = path.join(__dirname, "..", "..", "..", "music", "smusInstrument");

exports.preSteps = [
	() => (state, p, cb) =>
	{
		state.smusWorkDir = fileUtil.generateTempFilePath();

		tiptoe(
			function findInstruments()
			{
				fileUtil.glob(INSTRUMENT_DIR_PATH, "*", {nodir : true}, this.parallel());
				fileUtil.glob(path.resolve(path.join(path.dirname(state.input.absolute), "..")), path.join("Instruments", "*"), {nodir : true, nocase : true}, this.parallel());
				fs.mkdir(path.join(state.smusWorkDir, "Instruments"), {recursive : true}, this.parallel());
			},
			function prepareSMUSFileAndInstruments(standardInstrumentFilePaths, songInstrumentFilePaths)
			{
				[...standardInstrumentFilePaths, ...songInstrumentFilePaths].serialForEach((instrumentSrcFilePath, subcb) =>
				{
					const instrumentDestFilePath = path.join(state.smusWorkDir, "Instruments", path.basename(instrumentSrcFilePath));
					if(fs.existsSync(instrumentDestFilePath))
						return setImmediate(subcb);

					fs.symlink(instrumentSrcFilePath, instrumentDestFilePath, subcb);
				}, this.parallel());

				fs.copyFile(state.input.absolute, path.join(state.smusWorkDir, "in.smus"), this.parallel());
			},
			cb
		);
	}
];

exports.converterPriority =
[
	{program : "uade123", argsd : state => (["./in.smus", path.join(state.output.absolute, "outfile.wav")]), runOptions : state => ({cwd : state.smusWorkDir}) },
	["smus2midi", {program : "dexvert", flags : {asFormat : "music/mid", deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.mid`), state.output.absolute])}],
	["smusmidi", {program : "dexvert", flags : {asFormat : "music/mid", deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.mid`), state.output.absolute])}]
];

exports.postSteps = [
	(state, p) =>
	{
		const smusWorkDir = state.smusWorkDir;
		delete state.smusWorkDir;
		return p.util.file.unlink(smusWorkDir);
	}
];

*/
