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
	magic   : ["SMUS IFF Simple Musical Score", "IFF data, SMUS simple music"]
};

const INSTRUMENT_DIR_PATH = path.join(__dirname, "..", "..", "..", "music", "smusInstrument");

exports.steps =
[
	() => (state, p, cb) =>
	{
		const tmpWorkDir = fileUtil.generateTempFilePath(state.tmpDirPath);

		tiptoe(
			function findInstruments()
			{
				fileUtil.glob(INSTRUMENT_DIR_PATH, "*", {nodir : true}, this.parallel());
				fileUtil.glob(path.resolve(path.join(path.dirname(state.input.absolute), "..")), path.join("Instruments", "*"), {nodir : true, nocase : true}, this.parallel());
				fs.mkdir(path.join(tmpWorkDir, "Instruments"), {recursive : true}, this.parallel());
			},
			function prepareSMUSFileAndInstruments(standardInstrumentFilePaths, songInstrumentFilePaths)
			{
				[...standardInstrumentFilePaths, ...songInstrumentFilePaths].serialForEach((instrumentSrcFilePath, subcb) =>
				{
					const instrumentDestFilePath = path.join(tmpWorkDir, "Instruments", path.basename(instrumentSrcFilePath));
					if(fs.existsSync(instrumentDestFilePath))
						return setImmediate(subcb);

					fs.symlink(instrumentSrcFilePath, instrumentDestFilePath, subcb);
				}, this.parallel());

				fs.copyFile(state.input.absolute, path.join(tmpWorkDir, "in.smus"), this.parallel());
			},
			function performConversion()
			{
				p.util.program.run("uade123", {argsd : ["./in.smus", "./outfile.wav"], runOptions : {cwd : tmpWorkDir}})(state, p, this);
			},
			function cleanup()
			{
				if(!fileUtil.existsSync(path.join(tmpWorkDir, "outfile.wav")))
					return this();

				fileUtil.move(path.join(tmpWorkDir, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`), this);
			},
			function removeWorkDir()
			{
				fileUtil.unlink(tmpWorkDir, this);
			},
			cb
		);
	},
	(state, p) => p.util.file.findValidOutputFiles(),
	(state, p) => p.family.validateOutputFiles
];
