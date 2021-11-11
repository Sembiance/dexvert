import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {imageUtil, fileUtil} from "xutil";
import {DOMParser} from "https://deno.land/x/deno_dom@v0.1.17-alpha/deno-dom-native.ts";

export class image extends Family
{
	metaids = ["image", "darkTable", "ansiArt"];
	outExt = ".png";

	// gets meta information for the given input and format
	async getMeta(inputFile, format)
	{
		if(!format.metaProviders)
			return;

		const meta = {};

		// imageMagick meta provider
		if(format.metaProviders.includes("image"))
			Object.assign(meta, await imageUtil.getInfo(inputFile.absolute));

		if(format.metaProviders.includes("ansiArt"))
		{
			// ansiArt, we convert with deark to html and then parse the HTML for meta info about the ansi art file
			const r = await Program.runProgram("deark", inputFile, {flags : {charOutType : "html"}});
			if(r.f.new)
			{
				const htmlRaw = await fileUtil.readFile(r.f.new.absolute);
				const doc = new DOMParser().parseFromString(htmlRaw, "text/html");
				Array.from(doc.querySelectorAll("table.htt td.htc")).forEach(metaCell =>
				{
					const key = (metaCell.querySelector("span.hn") || {textContent : ""}).textContent.trim().trimChars(":");
					const val = (metaCell.querySelector("span.hv") || {textContent : ""}).textContent.trim().trimChars(":");
					if(key && val && key.length>0 && val.length>0)
						meta[key.toLowerCase()] = val;
				});
			}
		}

		return meta;
	}
}

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	C = require("../C.js"),
	domino = require("domino"),
	dexUtil = require("../dexUtil.js"),
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
		state.converters = dexUtil.preProcessConverters(state, p, p.format.converterPriority);

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
	
	if(p.format.meta.untrustworthy)
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

				// SVG's are VERY problematic for imagemagick to deal with. Loading up inkscape in the background and spinning at 100% CPU for ages while it renders some 65,000px wide SVG
				// So we don't even bother doing getImageInfo/identify and we just load up the file, parse as XML and deduce width/height from that
				// We can also check to make sure it actually has sub-elements, sometimes totalCADConverterX for example will produce an empty <svg></svg> file (NUTBOLT.DWG)
				if(dexid.formatid==="svg")
				{
					this.data.isSVG = true;
					p.util.program.run("svgInfo", {argsd : [outFilePath]})(state, p, (err, svgInfoResult) => this(err, (svgInfoResult || {}).meta || {}));
				}
				else
				{
					imageUtil.getInfo(outFilePath, {timeout : XU.SECOND*30}, this);
				}
			},
			function classifyImage(info)
			{
				// If we don't have a width or height, or we are an unsafe converter and are just a solid color, count the image as failed and remove it
				if(!info || !info.width || !info.height ||
				   ((unsafeConverter || untrustworthyConversion) && info.colorCount<=1 && (info.opaque===true || untrustworthyConversion)) ||	// Unsafe conversions must have 2 or more colors
				   (untrustworthyConversion && (info.width>20000 || info.height>20000)) ||
				   (p.format.outputValidator && !p.format.outputValidator(state, p, outSubPath, info)) ||
				   (this.data.isSVG && info.colorCount<=1))
				{
					if(state.verbose>=3)
						XU.log`Removing image ${outFilePath} due to not having width/height or no imageInfo or suspect imageInfo ${{unsafeConverter, untrustworthyConversion, info}}`;
					removeFile = true;
					return this.jump(-1);
				}


				let skipClassificationReason = null;

				// Only classify these image types
				if(!["gif", "png", "jpg", "webp", "svg"].includes(dexid.formatid))
					skipClassificationReason = `Unsupported image formatid: ${dexid.formatid}`;
				
				// Don't classify if the full original absolute path or formatid includes any of these names as it will likely come back as a false positive as they tend to look like "noise"
				if(C.TENSOR_EXCLUSIONS.some(v => dexid.formatid.toLowerCase().includes(v) || state.input.absolute.toLowerCase().includes(v)))
					skipClassificationReason = `Contains a known 'noisy' pattern in file path`;
				
				// Don't classify if the dimensions are too big
				if([info.width, info.height].some(v => v>=6000))
					skipClassificationReason = `Width or height is too big ${info.width}x${info.height}`;

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

// Standard inputMeta function for RAW dark table supported images
exports.darkTableInputMeta = function darkTableInputMeta(state, p, cb)
{
	tiptoe(
		function runDarkTableRSIdentify()
		{
			p.util.program.run("darktable-rs-identify")(state, p, this);
		},
		function recordMeta({meta : darkTableMeta}={})
		{
			if(Object.keys(darkTableMeta).length>0)
			{
				if(darkTableMeta.dimUncropped && darkTableMeta.dimUncropped.split("x").length===2)
					state.input.meta.image = { width : +darkTableMeta.dimUncropped.split("x")[0], height : +darkTableMeta.dimUncropped.split("x")[1] };
				state.input.meta.darkTable = darkTableMeta;
			}

			this();
		},
		cb
	);
};

*/
