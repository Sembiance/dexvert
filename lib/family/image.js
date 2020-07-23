"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	imageUtil = require("@sembiance/xutil").image;

function checkShouldContinue(state)
{
	return !state.output.files && state.imageConverters.length>0;
}

exports.imageAlchemy =
[
	(state, p) => p.util.dos.run({p, bin : "ALCHEMY.EXE", autoExec : [`ALCHEMY.EXE -t ${state.input.filePath} ${state.output.dirPath}\\OUT.TIF`]}),
	(state, p) => p.util.program.run(p.program.convert, {runOptions : {cwd : state.output.absolute}, args : ["OUT.TIF", "outfile.png"]}),
	(state, p) => p.util.file.unlink(path.join(state.output.absolute, "OUT.TIF"))
];

const converterPrograms =
[
	{program : "nconvert"},
	{program : "convert"},
	{program : "deark"},
	{program : "abydosconvert"},
	{program : "recoil2png"},
	{program : "ffmpeg"},
	exports.imageAlchemy,
	{program : "unoconv"}
];

const converterSteps =
[
	(state, p) =>
	{
		state.imageConverters = converterPrograms.slice().multiSort(cp => (Object.isObject(cp) && (p.format.converterPriorty || []).includes(cp.program) ? (p.format.converterPriorty || []).indexOf(cp.program) : 999));
		state.imageConverters.filterInPlace(cp =>
		{
			// abydos requires a mime type
			if(Object.isObject(cp) && cp.program==="abydosconvert" && !p.format.meta.mimeType)
				return false;
			
			return true;
		});

		return p.util.flow.noop;
	},
	(state0, p0) => p0.util.flow.batchRepeatUntil([
		(state, p) =>
		{
			state.imageConverter = state.imageConverters.shift();
			if(Array.isArray(state.imageConverter))
				return p.util.flow.serial(state.imageConverter);

			return state.imageConverter;
		},
		(state, p) => p.util.file.findValidOutputFiles(),
		() => exports.validateOutputImages], checkShouldContinue)
];

exports.steps = [(state, p) => p.util.flow.serial(p.format.steps || converterSteps)];

exports.validateOutputImages = function validateOutputImages(state, p, cb)
{
	(state.output.files || []).slice().parallelForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		tiptoe(
			function getImageInfo()
			{
				imageUtil.getInfo(outFilePath, this);
			},
			function removeIfNeeded(imageInfo)
			{
				if(imageInfo.width && imageInfo.height)
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

// Standard inputMeta function for images we support
exports.supportedImageInputMeta = function supportedImageInputMeta(state, p, cb)
{
	tiptoe(
		function getImageInfo()
		{
			imageUtil.getInfo(state.input.absolute, this);
		},
		function stashResults(imageInfo)
		{
			if(imageInfo && imageInfo.width && imageInfo.height)
			{
				state.input.meta[state.id.formatid] = imageInfo;
				state.processed = true;
			}

			this();
		},
		cb
	);
};
