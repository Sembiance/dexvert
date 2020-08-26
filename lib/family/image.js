"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	domino = require("domino"),
	fileUtil = require("@sembiance/xutil").file,
	imageUtil = require("@sembiance/xutil").image;

function checkShouldContinue(state)
{
	return !state.output.files && state.converters.length>0;
}

exports.imageAlchemy =
[
	(state, p) => p.util.dos.run({p, bin : "ALCHEMY.EXE", autoExec : [`ALCHEMY.EXE -t ${state.input.filePath} OUT.TIF`]}),
	(state, p) => p.util.program.run("convert", {args : p.program.convert.args(state, p, "OUT.TIF")})
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
	{program : "inkscape"},
	{program : "bpgdec"},
	{program : "xcf2png"},
	{program : "avifdec"},
	{program : "h5topng"},
	{program : "gdtopng"},
	{program : "gd2topng"},
	{program : "cistopbm"},
	{program : "dxf-to-svg"},
	{program : "fig2dev"},
	{program : "unoconv"},
	{program : "ansilove"}
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
				const excplictlyIncluded = (p.format.converterPriorty || []).includes(cp.program);
				
				// Check to see if we've excluded this program
				if((p.format.converterExclude || []).includes(cp.program) || ((p.format.converterExclude || []).includes("*") && !excplictlyIncluded))
					return false;

				// abydos requires a mime type
				if(cp.program==="abydosconvert" && !p.format.meta.mimeType)
					return false;
				
				// Some converter programs are not safe for all images, so only include if it was explicitly specified in the format's converterPriority list
				if(p.program[cp.program].meta.bruteUnsafe && !excplictlyIncluded)
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
	if((state.output.files || []).length===0)
		delete state.converter;

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
				{
					delete state.output.files;
					delete state.converter;
				}
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
				if(p.format.meta.browserNative)
					state.processed = true;
			}

			this();
		},
		cb
	);
};

// Standard inputMeta function for images we support
exports.ansiArtInputMeta = function ansiArtInputMeta(state, p, cb)
{
	tiptoe(
		function convertWithDeark()
		{
			state.dearkCharOutput = "html";
			p.util.program.run("deark", {args : p.program.deark.args(state, p, state.input.filePath, state.cwd)})(state, p, this);
		},
		function parseHTMLForMeta()
		{
			delete state.dearkCharOutput;
			
			const htmlFilePath = path.join(state.cwd, `${state.input.name}.000.html`);

			if(!fileUtil.existsSync(htmlFilePath))
				return this.finish();

			const doc = domino.createWindow(fs.readFileSync(htmlFilePath, XU.UTF8)).document;
			const meta = {};

			Array.from(doc.querySelectorAll("table.htt td.htc")).forEach(metaCell =>
			{
				const key = (metaCell.querySelector("span.hn") || {textContent : ""}).textContent.trim().trimChars(":");
				const val = (metaCell.querySelector("span.hv") || {textContent : ""}).textContent.trim().trimChars(":");
				if(key && val && key.length>0 && val.length>0)
					meta[key.toLowerCase()] = val;
			});

			if(Object.keys(meta).length>0)
				state.input.meta.ansiArt = meta;
			
			this();
		},
		cb
	);
};
