"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	dexvert = require("../dexvert.js"),
	fileUtil = require("@sembiance/xutil").file;

exports.steps =
[
	(state, p) => (p.format.steps ? p.util.flow.serial(p.format.steps) : p.util.flow.noop),
	(state, p) => p.format.post || p.util.flow.noop,
	(state, p) => p.util.file.findValidOutputFiles(),
	() => exports.convertOutputFiles,
	(state, p) => p.util.file.findValidOutputFiles(true),
	() => exports.validateOutputFiles
];

exports.convertOutputFiles = function convertOutputFiles(state, p, cb)
{
	(state.output.files || []).slice().parallelForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		tiptoe(
			function identifyOutputFile()
			{
				dexvert.identify(outFilePath, this);
			},
			function convertToFlacIfNeeded(outputInfo)
			{
				if(!outputInfo.some(match => match.from==="dexvert" && match.formatid==="wav"))
					return this.finish();

				p.util.program.run("ffmpeg", {argsd : [outFilePath, path.join(path.dirname(outFilePath), `${path.basename(outFilePath, path.extname(outFilePath))}.flac`)]})(state, p, this);
			},
			function removeOriginalWAV()
			{
				fileUtil.unlink(outFilePath, this);
			},
			subcb
		);
	}, cb);
};

exports.validateOutputFiles = function validateOutputFiles(state, p, cb)
{
	// Don't run as parallelForEach() because soxi depends on asynchronous post checking of output
	(state.output.files || []).slice().serialForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		tiptoe(
			function getAudioInfo()
			{
				p.util.program.run("soxi", {argsd : [outFilePath]})(state, p, this);
			},
			function removeIfNeeded()
			{
				if(state.run.meta.soxi && state.run.meta.soxi.sampleEncoding)
				{
					delete state.run.meta.soxi;
					return this();
				}

				if(state.verbose>=1)
					XU.log`Invalid audio output file ${outFilePath} with sox info: ${state.run.meta.soxi} ${fs.statSync(outFilePath).size}`;
				
				state.output.files.removeOnce(outSubPath);
				if(state.output.files.length===0)
					delete state.output.files;
				fileUtil.unlink(outFilePath, this);
			},
			subcb
		);
	}, cb);
};

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	if(state.output.files)
		state.processed = true;

	if(p.format.updateProcessed)
		return p.format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};

// Standard inputMeta function for audio files
exports.supportedInputMeta = function supportedInputMeta(state, p, cb)
{
	tiptoe(
		function getAudioInfo()
		{
			p.util.program.run("soxi")(state, p, this);
		},
		function stashResults()
		{
			if(state.run.meta.soxi)
			{
				state.input.meta.audio = state.run.meta.soxi;
				delete state.run.meta.soxi;
				if(!p.format.steps)
					state.processed = true;
			}

			this();
		},
		cb
	);
};
