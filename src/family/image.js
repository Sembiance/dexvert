"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	C = require("../C.js"),
	domino = require("domino"),
	dexvert = require("../dexvert.js"),
	fileUtil = require("@sembiance/xutil").file,
	tensorUtil = require("../../tensor/tensorUtil.js"),
	imageUtil = require("@sembiance/xutil").image;

function checkShouldContinue(state)
{
	return !state.output.files && state.converters.length>0;
}

exports.converterSteps =
[
	(state, p) =>
	{
		state.converters = ((typeof p.format.converterPriorty==="function" ? p.format.converterPriorty(state, p) : p.format.converterPriorty) || []).map(v => (Object.isObject(v) ? v : {program : v}));

		state.converters.filterInPlace(cp =>
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
			state.converter = state.converters.shift();
			if(Array.isArray(state.converter))
				return p.util.flow.serial(state.converter);

			return state.converter;
		},
		(state, p) => p.util.file.findValidOutputFiles(),
		() => exports.validateOutputFiles], checkShouldContinue)
];

exports.steps =
[
	(state, p) => p.util.flow.serial(p.format.steps || exports.converterSteps),
	(state, p) => (p.format.steps ? p.util.file.findValidOutputFiles() : p.util.flow.noop),
	(state, p) => (p.format.steps ? exports.validateOutputFiles : p.util.flow.noop)
];

exports.validateOutputFiles = function validateOutputFiles(state, p, cb)
{
	if((state.output.files || []).length===0)
		delete state.converter;

	const unsafeConverter = p.program?.[state.converter?.program]?.meta?.unsafe;
	let untrustworthyConversion = false;

	// If the converter we used marked it's conversion as untrustworthy (convert.js on a read error for example) then we mark it as such here
	if(state.converter?.program && (p.util.program.getRan(state, state.converter.program) || {})?.untrustworthyConversion)
		untrustworthyConversion = true;

	(state.output.files || []).slice().parallelForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		let removeFile = false;
		let dexid = null;
		tiptoe(
			function identifyOutputFile()
			{
				dexvert.identify(outFilePath, {tmpFilePath : state.tmpFilePath}, this);
			},
			function getImageInfo(outIdentifications)
			{
				dexid = (outIdentifications || []).find(o => o.from==="dexvert");
				if(!dexid || dexid.family!=="image")
				{
					if(state.verbose>=3)
						XU.log`Removing image ${outFilePath} due to not being identified as an image ${{dexid}}`;
					removeFile = true;
					return this.jump(-1);
				}

				const imageGetInfoOptions = {timeout : XU.SECOND*30};
				if(dexid.formatid==="svg")
					imageGetInfoOptions.svg = true;
				imageUtil.getInfo(outFilePath, imageGetInfoOptions, this);
			},
			function classifyImage(imageInfo)
			{
				// If we don't have a width or height, or we are an unsafe converter and are just a solid color, count the image as failed and remove it
				if(!imageInfo || !imageInfo.width || !imageInfo.height || ((unsafeConverter || untrustworthyConversion) && imageInfo.colorCount===1 && imageInfo.opaque===true))
				{
					if(state.verbose>=3)
						XU.log`Removing image ${outFilePath} due to not having width/height or no imageInfo or suspect imageInfo ${{unsafeConverter, untrustworthyConversion, imageInfo}}`;
					removeFile = true;
					return this.jump(-1);
				}


				let skipClassificationReason = null;

				// Only classify these image types
				if(!["gif", "png", "jpg", "webp", "svg"].includes(dexid.formatid))
					skipClassificationReason = `Unsupported image formatid: ${dexid.formatid}`;
				
				// Don't classify if the full original absolute path includes any of these names as it will likely come back as a false positive as they tend to look like "noise"
				if(["texture", "stereo", "pattern", "brush", "noise", "illusion"].some(v => state.input.absolute.toLowerCase().includes(v)))
					skipClassificationReason = `Contains a known 'noisy' pattern in file path`;
				
				// Don't classify if the dimensions are too big
				if([imageInfo.width, imageInfo.height].some(v => v>=6000))
					skipClassificationReason = `Width or height is too big ${imageInfo.width}x${imageInfo.height}`;

				// tensorUtil.classifyImage will convert these into PNG before sending to the classifier.
				// We skip some files from classification, due to them looking like garbage. We do this by hoping the input file path contains certain keywords that are known to have 'noisy' images
				if(!skipClassificationReason)
				{
					if(state.verbose>=4)
						XU.log`Getting garbage classification for image: ${outFilePath}`;

					tensorUtil.classifyImage(outFilePath, "garbage", this);
				}
				else
				{
					if(state.verbose>=4)
						XU.log`SKIPPING garbage classification for image: ${outFilePath} due to: ${skipClassificationReason}`;
					this.jump(2);
				}
			},
			function checkImageValidity(garbageResult)
			{
				if(garbageResult && garbageResult.confidence>0)
				{
					if(!state.output.hasOwnProperty("garbageProbability"))
						state.output.garbageProbability = {};
					state.output.garbageProbability[`${state.id.family}/${state.id.formatid}:${outSubPath}`] = garbageResult.confidence;
				}

				if(!garbageResult)
					throw new Error(`Failed to calculate garbage probability for: ${outFilePath} with result: ${garbageResult}`);

				if(garbageResult.confidence>C.MATCH_MAX_GARBAGE_PROBABILITIES[state.id.matchType])
				{
					if(state.verbose>=3)
						XU.log`Removing image ${outFilePath} due to detected as garbage: ${garbageResult}`;
						
					fs.copyFileSync(outFilePath, path.join(C.GARBAGE_DETECTED_DIR_PATH, `${garbageResult.confidence.noExponents()}-${Math.randomInt(1, 100000)}-${Date.now().toString()}-${state.id.formatid}-${state.input.absolute.replaceAll("/", ":")}-${outSubPath}`));
					removeFile = true;
					return this.jump(-1);
				}

				this();
			},
			function removeIfNeeded()
			{
				if(!removeFile)
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
	else
		delete state.converter;

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
			const imageGetInfoOptions = {timeout : XU.MINUTE*3};
			if(state?.id?.formatid==="svg")
				imageGetInfoOptions.svg = true;
			imageUtil.getInfo(state.input.absolute, imageGetInfoOptions, this);
		},
		function stashResults(imageInfo)
		{
			if(imageInfo?.width && imageInfo.height)
			{
				state.input.meta.image = imageInfo;
				if(p.format.meta.untouched)
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
			p.util.program.run("deark", {flags : {dearkCharOutput : "html"}, argsd : [state.input.filePath, state.cwd]})(state, p, this);
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
