#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	path = require("path"),
	cmdUtil = require("@sembiance/xutil").cmd,
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	MidiWriter = require("midi-writer-js");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <inputFilePath> soundFont2 file into multiple MIDI files, 1 per instrument",
	args :
	[
		{argid : "inputFilePath", desc : "File path to identify", required : true},
		{argid : "outputDirectory", desc : "Output directory to output MIDI files to", required : true}
	]});

const midiFilePaths = [];

tiptoe(
	function ensureLoaded()
	{
		runUtil.run("fluidsynth", ["--audio-driver=file", argv.inputFilePath], {silent : true, inputData : "fonts\nquit"}, this);
	},
	function runFluidSynth(fluidSynthRaw)
	{
		if(!fluidSynthRaw.includes(path.basename(argv.inputFilePath)) || ["/usr/share/sounds/sf2/FluidR3_G", "Failed to load SoundFont", "not a SoundFont or MIDI file or error occurred identifying it"].some(v => fluidSynthRaw.includes(v)))
		{
			console.error("Failed to load soundfont into FluidSynth.");
			return this.finish();
		}

		runUtil.run("fluidsynth", ["--audio-driver=file", "--quiet", argv.inputFilePath], {silent : true, "ignore-stderr" : true, inputData : "inst 1\nquit"}, this);
	},
	function writeMidiFiles(fluidSynthRaw)
	{
		const meta = {banks : {}};
		(fluidSynthRaw || "").trim().split("\n").forEach(line =>
		{
			if(!(/^\d/).test(line))
				return;
			
			const props = (line.match(/(?<bank>\d+)-(?<preset>\d+)\s(?<name>.+)$/) || {})?.groups;
			if(!props)
				return;
			
			if(!meta.banks[+props.bank])
				meta.banks[+props.bank] = {};
			meta.banks[+props.bank][+props.preset] = props.name;
		});

		if(!meta?.banks || Object.keys(meta.banks).length===0)
			return this.finish();

		const po = 3;	// octave to play puff at
		Object.entries(meta.banks).flatMap(([bank, presets]) => Object.entries(presets).map(([preset, name]) => ({bank, preset, name}))).parallelForEach((o, subcb) =>
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

			midiFilePaths.push(path.join(argv.outputDirectory, `${o.bank.toString().padStart(3, "0")}-${o.preset.toString().padStart(3, "0")} - ${o.name.replaceAll("/", "-")}.mid`));
			fs.writeFile(midiFilePaths.last(), new MidiWriter.Writer(track).buildFile(), subcb);
		}, this.parallel());

		fileUtil.unlink(path.join(process.cwd(), "fluidsynth.wav"), this.parallel());
	},
	XU.FINISH
);
