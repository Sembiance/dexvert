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

exports.irfanView =
[
	(state, p) => p.util.wine.run({cmd : "IrfanView/i_view32.exe", args : [p.util.wine.path(path.join(state.cwd, state.input.filePath)), "/silent", `/convert=${p.util.wine.path(path.join(state.cwd, "out.png"))}`], timeout : XU.MINUTE*10}),
	(state, p) => p.util.file.move(path.join(state.cwd, "out.png"), path.join(state.output.absolute, `${state.input.name}.png`))
];

exports.imageAlchemy =
[
	(state, p) => p.util.dos.run({p, bin : "ALCHEMY.EXE", autoExec : [`ALCHEMY.EXE -t ${state.input.filePath} OUT.TIF`]}),
	() => ({program : "convert", argsd : ["OUT.TIF"]})
];

const DEFAULT_CONVERTERS =
[
	"nconvert",
	"convert",
	"abydosconvert",
	"recoil2png",
	"deark",		// While deark is awesome, it always tends to add suffix counts like .000.png even with just 1 image. So it's priority order is a bit lower due to this
	"ffmpeg",
	"uniconvertor",
	"inkscape",
	"bpgdec",
	"xcf2png",
	"avifdec",
	"h5topng",
	"gdtopng",
	"gd2topng",
	"cistopbm",
	"dxf-to-svg",
	"fig2dev",
	"unoconv",
	"ansilove"
];

exports.converterSteps =
[
	(state, p) =>
	{
		state.converters = (p.format.converterPriorty || []).map(v => (Object.isObject(v) ? v : {program : v}));

		// Now add our DEFAULT_CONVERTERS so long as we are not excluding all defaults (["*"]) and it's not explictly excluded or already included
		if(!(p.format.converterExclude || []).includes("*"))
			state.converters.push(...DEFAULT_CONVERTERS.filter(d => !(p.format.converterExclude || []).includes(d) && !state.converters.find(c => c.program===d) && !p.program[d].meta.bruteUnsafe).map(d => ({program : d})));

		state.converters.filterInPlace(cp =>
		{
			if(Object.isObject(cp))
			{
				// abydos requires a mime type
				if(cp.program==="abydosconvert" && !p.format.meta.mimeType)
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
			p.util.program.run("deark", {stateFlags : {dearkCharOutput : "html"}, argsd : [state.input.filePath, state.cwd]})(state, p, this);
		},
		function parseHTMLForMeta()
		{
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
