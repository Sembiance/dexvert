"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file;

function checkShouldContinue(state)
{
	return !state.output.files && state.converters.length>0;
}

const converterPrograms =
[
	{program : "xmp"},
	{program : "mikmod2wav"},
	{program : "openmpt123"},
	{program : "uade123"},
	{program : "adplay"}
];

exports.converterSteps =
[
	(state, p) =>
	{
		state.converters = converterPrograms.slice().multiSort(cp => (Object.isObject(cp) && (p.format.converterPriorty || []).includes(cp.program) ? (p.format.converterPriorty || []).indexOf(cp.program) : 999));
		return p.util.flow.noop;
	},
	(state0, p0) => p0.util.flow.batchRepeatUntil([
		(state, p) =>
		{
			state.converter = state.converters.shift();
			if(Array.isArray(state.converter))
				return p.util.flow.serial(state.converter);

			return state.converter;
		},
		(state, p) => p.util.file.findValidOutputFiles(),
		() => exports.validateOutputFiles], checkShouldContinue)
];

exports.steps = [(state, p) => p.util.flow.serial(p.format.steps || exports.converterSteps)];

exports.validateOutputFiles = function validateOutputFiles(state, p, cb)
{
	(state.output.files || []).slice().parallelForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		tiptoe(
			function getOutputInfo()
			{
				p.util.program.run("sox", {args : [outFilePath, "-n", "stat"]})(state, p, this);
			},
			function convertOrRemove()
			{
				const soxStats = state.run.sox[0].trim().split("\n").reduce((r, line="") =>
				{
					const parts = line.split(":");
					if(!parts || parts.length!==2)
						return r;
					r[parts[0].split(" ").filterEmpty().map(v => v.trim()).join(" ")] = parts[1].trim();
					return r;
				}, {});

				if(soxStats["Maximum amplitude"]==="0.000000" && soxStats["Minimum amplitude"]==="0.000000" && soxStats["Midline amplitude"]==="0.000000")
				{
					state.output.files.removeOnce(outSubPath);
					if(state.output.files.length===0)
						delete state.output.files;

					return fileUtil.unlink(outFilePath, this.finish);
				}
				
				state.ffmpegExt = ".flac";
				p.util.program.run("ffmpeg", {args : p.program.ffmpeg.args(state, p, outFilePath, path.join(path.dirname(outFilePath), `${path.basename(outFilePath, path.extname(outFilePath))}.flac`))})(state, p, this);
			},
			function removeOriginalWAV()
			{
				delete state.ffmpegExt;
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

	if(Object.keys(state.input.meta.music || {}).length===0)
		delete state.input.meta.music;

	setImmediate(cb);
};

// Standard inputMeta function for music files we support
exports.supportedInputMeta = function supportedInputMeta(state, p, cb)
{
	tiptoe(
		function getMusicInfo()
		{
			p.util.program.run("modInfo")(state, p, this);
		},
		function stashResults()
		{
			if(state.run.meta.modInfo)
			{
				state.input.meta.music = state.run.meta.modInfo;
				delete state.run.meta.modInfo;
			}

			this();
		},
		cb
	);
};
