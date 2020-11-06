"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file;

function checkShouldContinue(state)
{
	return !state.output.files && state.converters.length>0;
}

const DEFAULT_CONVERTERS =
[
	"xmp",
	"mikmod2wav",
	"openmpt123",
	"uade123",
	"adplay"
];

exports.converterSteps =
[
	(state, p) =>
	{
		state.converters = (p.format.converterPriorty || []).map(v => (Object.isObject(v) ? v : {program : v}));

		// Now add our DEFAULT_CONVERTERS so long as we are not excluding all defaults (["*"]) and it's not explictly excluded or already included
		if(!(p.format.converterExclude || []).includes("*"))
			state.converters.push(...DEFAULT_CONVERTERS.filter(d => !(p.format.converterExclude || []).includes(d) && !state.converters.find(c => c.program===d) && !p.program[d].meta.bruteUnsafe).map(d => ({program : d})));

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
				const r = p.util.program.getRan(state, "sox");
				const soxStats = (r.results || "").trim().split("\n").reduce((result, line="") =>
				{
					const parts = line.split(":");
					if(!parts || parts.length!==2)
						return result;
					result[parts[0].split(" ").filterEmpty().map(v => v.trim()).join(" ")] = parts[1].trim();
					return result;
				}, {});

				if(soxStats["Maximum amplitude"]==="0.000000" && soxStats["Minimum amplitude"]==="0.000000" && soxStats["Midline amplitude"]==="0.000000")
				{
					state.output.files.removeOnce(outSubPath);
					if(state.output.files.length===0)
						delete state.output.files;

					return fileUtil.unlink(outFilePath, this.finish);
				}
				
				p.util.program.run("ffmpeg", {stateFlags : {ffmpegExt : ".flac"}, argsd : [outFilePath, path.join(path.dirname(outFilePath), `${path.basename(outFilePath, path.extname(outFilePath))}.flac`)]})(state, p, this);
			},
			function removeOriginalWAV()
			{
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
			if(p.util.program.getMeta(state, "modInfo"))
				state.input.meta.music = p.util.program.getMeta(state, "modInfo");

			this();
		},
		cb
	);
};
