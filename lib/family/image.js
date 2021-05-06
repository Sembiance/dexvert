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

exports.steps = [(state, p) => p.util.flow.serial(p.format.steps || exports.converterSteps)];

exports.validateOutputFiles = function validateOutputFiles(state, p, cb)
{
	if((state.output.files || []).length===0)
		delete state.converter;

	const unsafeConverter = p.program?.[state.converter?.program]?.meta?.unsafe;

	(state.output.files || []).slice().parallelForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		let removeFile = false;
		tiptoe(
			function identifyOutputFile()
			{
				dexvert.identify(outFilePath, {tmpFilePath : state.tmpFilePath}, this);
			},
			function classifyImage(outIdentifications)
			{
				const dexid = (outIdentifications || []).find(o => o.from==="dexvert");
				if(!dexid || dexid.family!=="image")
				{
					removeFile = true;
					return this.jump(-1);
				}

				imageUtil.getInfo(outFilePath, {timeout : XU.SECOND*30}, this.parallel());

				// tensorUtil.classifyImage will convert these into PNG before sending to the classifier.
				// We skip some files from classification, due to them looking like garbage. We do this by hoping the input file path contains certain keywords that are known to have 'noisy' images
				if(["gif", "png", "jpg", "webp", "svg"].includes(dexid.formatid) && !["texture", "stereo", "pattern", "brush", "noise", "illusion"].some(v => state.input.absolute.toLowerCase().includes(v)))
				{
					if(state.verbose>=4)
						XU.log`Getting garbage classification for image: ${outFilePath}`;

					tensorUtil.classifyImage(outFilePath, "garbage", this.parallel());
				}
				else
				{
					this.parallel()(undefined, []);
				}
			},
			function checkImageValidity(imageInfo, [garbageResult])
			{
				// If we don't have a widht or height, or we are an unsafe converter and are just a solid color, count the image as failed and remove it
				if(!imageInfo || !imageInfo.width || !imageInfo.height || (unsafeConverter && imageInfo.colorCount===1 && imageInfo.opaque===true))
				{
					removeFile = true;
					return this.jump(-1);
				}

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
			imageUtil.getInfo(state.input.absolute, {timeout : XU.MINUTE*3}, this);
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
