"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	imageUtil = require("@sembiance/xutil").image;

function checkShouldContinue(state)
{
	return !state.output.files && state.converters.length>0;
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
	{program : "abydosconvert"},
	{program : "recoil2png"},
	{program : "deark"},		// While deark is awesome, it always tends to add suffix counts like .000.png even with just 1 image. So it's priority order is a bit lower due to this
	{program : "ffmpeg"},
	{program : "uniconvertor"},
	{program : "bpgdec"},
	{program : "xcf2png"},
	{program : "avifdec"},
	{program : "h5topng"},
	{program : "gdtopng"},
	{program : "gd2topng"},
	{program : "dxf-to-svg"},
	exports.imageAlchemy,
	{program : "unoconv", unsafe : true},
	{program : "ansilove", unsafe : true}
];

exports.converterSteps =
[
	(state, p) =>
	{
		state.converters = converterPrograms.slice().multiSort(cp => (Object.isObject(cp) && (p.format.converterPriorty || []).includes(cp.program) ? (p.format.converterPriorty || []).indexOf(cp.program) : 999));
		state.converters.filterInPlace(cp =>
		{
			if(Object.isObject(cp))
			{
				if((p.format.converterExclude || []).includes(cp.program))
					return false;

				// abydos requires a mime type
				if(cp.program==="abydosconvert" && !p.format.meta.mimeType)
					return false;
				
				// Some converter programs are not safe for all images, so only include if it was explicitly specified in the format's converterPriority list
				if(cp.unsafe && !(p.format.converterPriorty || []).includes(cp.program))
					return false;
			}
			
			return true;
		});

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
			function getImageInfo()
			{
				imageUtil.getInfo(outFilePath, {simpleOnly : true}, this);
			},
			function removeIfNeeded(imageInfo)
			{
				if(imageInfo && imageInfo.width && imageInfo.height)
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
exports.supportedInputMeta = function supportedInputMeta(state, p, cb)
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
				state.input.meta.image = imageInfo;
				state.processed = true;
			}

			this();
		},
		cb
	);
};
