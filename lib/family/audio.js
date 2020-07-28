"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	dexvert = require(path.join(__dirname, "..", "dexvert.js")),
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

				p.util.program.run(p.program.ffmpeg, {args : ["-i", outFilePath, "-c:a", "flac", "-compression_level", "12", path.join(path.dirname(outFilePath), `${path.basename(outFilePath, path.extname(outFilePath))}.flac`)]})(state, p, this);
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
	(state.output.files || []).slice().parallelForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		tiptoe(
			function getAudioInfo()
			{
				p.util.program.run(p.program.soxi, {args : [outFilePath]})(state, p, this);
			},
			function removeIfNeeded()
			{
				if(state.run.soxi && state.run.soxi.length>0 && state.run.soxi[0] && state.run.soxi[0].includes("Sample Encoding"))
					return this();
				
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
			p.util.program.run(p.program.soxi)(state, p, this);
		},
		function stashResults()
		{
			if(state.run.soxi && state.run.soxi.length>0 && state.run.soxi[0] && state.run.soxi[0].trim().length>0)
			{
				const meta = {};
				state.run.soxi[0].trim().split("\n").forEach(line =>
				{
					const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
					if(key && val && !["Input File", "Comments", "File Size"].some(v => key.trim().startsWith(v)))
					{
						const properKey = key.trim().toCamelCase();
						meta[properKey] = (["channels", "sampleRate"].some(v => properKey===v) ? +val.trim() : val.trim());
					}
				});

				if(Object.keys(meta).length>0)
				{
					state.input.meta.audio = meta;
					if(!p.format.steps)
						state.processed = true;
				}
			}

			this();
		},
		cb
	);
};
