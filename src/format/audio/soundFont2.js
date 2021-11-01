"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	path = require("path"),
	MidiWriter = require("midi-writer-js");

exports.meta =
{
	name           : "SoundFont 2.0",
	website        : "http://fileformats.archiveteam.org/wiki/SoundFont_2.0",
	ext            : [".sf2"],
	magic          : ["RIFF (little-endian) data SoundFont/Bank", "Standard SoundFont"],
	forbiddenMagic : ["Emu Sound Font (v1.0)"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		const midiFilePaths = [];

		tiptoe(
			function runSF2Info()
			{
				p.util.program.run("sf2info")(state, p, this);
			},
			function writeMidiFiles(r)
			{
				if(!r?.meta?.banks || Object.keys(r.meta.banks).length===0)
					return setImmediate(cb);

				state.input.meta[p.format.meta.formatid] = r.meta;
				state.processed = true;

				const po = 3;	// octave to play puff at
				Object.entries(r.meta.banks).flatMap(([bank, presets]) => Object.entries(presets).map(([preset, name]) => ({bank, preset, name}))).parallelForEach((o, subcb) =>
				{
					const track = new MidiWriter.Track();
					track.controllerChange(0, o.bank);
					track.addEvent(new MidiWriter.ProgramChangeEvent({instrument : o.preset}));

					[
						// Note progression
						...[2, 3, 4].flatMap((octave, octavei) => ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"].batch(3).map(subnotes => ({pitch : [`${subnotes[2-octavei]}${octave}`], duration : "8"}))),

						// Chords
						{pitch : ["C2", "E2", "G2"], duration : "2"},
						{pitch : ["C3", "E3", "G3"], duration : "2"},
						{pitch : ["C4", "E4", "G4"], duration : "2"},

						// Puff
						{pitch : [`D${po}`, `F${po}`, `A${po}`], duration : "d4"},
						{pitch : [`D${po}`], duration : "8"},
						{pitch : [`D${po}`], duration : "4"},
						{pitch : [`D${po}`], duration : "4"},
						{pitch : [`C#${po}`, `A${po}`, `C#${po+1}`, `F#${po+1}`], duration : "d4"},
						{pitch : [`A${po-1}`], duration : "d4"},
						{wait : "4", pitch : [`B${po-1}`, `G${po}`, `D${po}`], duration : "d4"},
						{pitch : [`D${po}`], duration : "d4"},
						{pitch : [`D${po}`], duration : "4"},
						{pitch : [`A${po-1}`, `F#${po}`, `D${po}`], duration : "4"}
					].forEach(note => track.addEvent(new MidiWriter.NoteEvent({...note, velocity : 100})));

					midiFilePaths.push(path.join(state.cwd, `${o.bank.toString().padStart(3, "0")}-${o.preset.toString().padStart(3, "0")} - ${o.name.replaceAll("/", "-")}.mid`));
					fs.writeFile(midiFilePaths.last(), new MidiWriter.Writer(track).buildFile(), subcb);
				}, this);
			},
			function convertMidiFiles()
			{
				const timidityOptions = {flags : {midiFont : state.input.absolute}};
				midiFilePaths.parallelForEach((midiFilePath, subcb) => p.util.program.run("timidity", {...timidityOptions, argsd : [midiFilePath, path.join(state.output.absolute, `${path.basename(midiFilePath, ".mid")}.wav`)]})(state, p, subcb), this);
			},
			cb
		);
	},
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.convertOutputFiles,
	(state, p) => p.family.validateOutputFiles
];
