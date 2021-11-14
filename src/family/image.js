import {xu, fg} from "xu";
import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {imageUtil, fileUtil} from "xutil";
import {DOMParser} from "https://deno.land/x/deno_dom@v0.1.17-alpha/deno-dom-native.ts";
import {classifyImage} from "../tensorUtil.js";
import * as path from "https://deno.land/std@0.114.0/path/mod.ts";

// These particular kinds of images often look like noise/static/garbage and are usually caught by the tensorflow garbage model
const TENSOR_PATH_EXCLUSIONS =
[
	"texture", "textura",
	"background", "backgrnd",
	"stereo", "pattern", "brush", "noise", "illusion", "fractal", "border"
];

const MATCH_MAX_GARBAGE_PROBABILITIES =
{
	magic    : 0.7,
	filename : 0.6,
	ext      : 0.6,
	fileSize : 0.01,
	fallback : 0.01
};

const GARBAGE_DETECTED_DIR_PATH = "/mnt/dexvert/garbageDetected";

export class image extends Family
{
	metaids = ["image", "darkTable", "ansiArt"];

	async verify(dexFile, identifications, {programid, verbose, dexState})
	{
		const dexid = identifications.find(id => id.from==="dexvert" && id.family==="image");
		if(!dexid)
		{
			if(verbose>=3)
				xu.log`DELETING OUTPUT due to not being identified as an image: ${dexFile.pretty()}`;
			return false;
		}

		const meta = {};
		// SVG's are VERY problematic for imagemagick to deal with. Loading up inkscape in the background and spinning at 100% CPU for ages while it renders some 65,000px wide SVG
		// So we don't even bother doing getImageInfo/identify and we just load up the file, parse as XML and deduce width/height from that
		// We can also check to make sure it actually has sub-elements, sometimes totalCADConverterX for example will produce an empty <svg></svg> file (NUTBOLT.DWG)
		if(dexid.formatid==="svg")
			console.log(await Program.runProgram("svgInfo", dexFile, {verbose}));	// TODO need to handle this
		else
			Object.assign(meta, await imageUtil.getInfo(dexFile.absolute));

		if(!meta.width || !meta.height)
			return false;

		if(Program.programs[programid].unsafe && meta.colorCount<=1 && meta.opaque)
			return false;

		if(Program.programs[programid].unsafe && [meta.width, meta.height].some(v => v>=15000))
			return false;

		if(dexid.formatid==="svg" && meta.colorCount<=1)
			return false;
		
		let skipTensor = null;

		// Only classify these image types
		if(!["gif", "png", "jpg", "webp", "svg"].includes(dexid.formatid))
			skipTensor = `Unsupported image formatid: ${dexid.formatid}`;
		
		// Don't classify if the full original absolute path or formatid includes any of these names as it will likely come back as a false positive as they tend to look like "noise"
		if(TENSOR_PATH_EXCLUSIONS.some(v => dexid.formatid.toLowerCase().includes(v) || dexState.original.input.absolute.toLowerCase().includes(v)))
			skipTensor = `Contains a known 'noisy' pattern in original file path`;
		
		// Don't classify if the dimensions are too big
		if([meta.width, meta.height].some(v => v>=6000))
			skipTensor = `Width or height is too big ${meta.width}x${meta.height}`;
		
		if(!skipTensor)
		{
			// tensorUtil.classifyImage will convert these into PNG before sending to the tensor
			const garbage = await classifyImage(dexFile.absolute, "garbage");
			if(typeof garbage!=="number" || garbage<0 || garbage>1)
				throw new Error(`Got invalid garabge result for ${dexFile.pretty()} ${dexState.original.input.pretty()} ${garbage}`);

			console.log(dexState.id.matchType);
			if((garbage || 0)>MATCH_MAX_GARBAGE_PROBABILITIES[dexState.id.matchType])
			{
				if(verbose>=3)
					xu.log`Image detected as ${fg.peach("garbage")} with val ${garbage} for: ${dexFile.pretty()} ${dexState.original.input.pretty()}`;
				await Deno.copyFile(dexFile.absolute, path.join(GARBAGE_DETECTED_DIR_PATH, `${garbage.noExponents()}-${Math.randomInt(1, 10000)}-${dexState.format.formatid}-${dexState.original.input.absolute.replaceAll("/", ":")}-${dexFile.rel.replaceAll("/", ":")}`));
				return false;
			}
		}
		else
		{
			if(verbose>=3)
				xu.log`image.verify is ${fg.orange("SKIPPING")} garbage classification: ${skipTensor}`;
		}

		return true;
	}

	// gets meta information for the given input and format
	async getMeta(inputFile, format, {verbose}={})
	{
		if(!format.metaProviders)
			return;

		const meta = {};
		for(const metaProvider of format.metaProviders)
		{
			if(verbose>=3)
				xu.log`image.getMeta() getting meta from provider ${metaProvider}`;

			// imageMagick meta provider
			if(metaProvider==="image")
				Object.assign(meta, await imageUtil.getInfo(inputFile.absolute));

			if(metaProvider==="ansiArt")
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
				await Deno.remove(r.f.outDir.absolute, {recursive : true});
				await Deno.remove(r.f.homeDir.absolute, {recursive : true});
			}

			if(metaProvider==="darkTable")
			{
				const r = await Program.runProgram("darktable_rs_identify", inputFile);
				if(r.meta?.dimUncropped && r.meta.dimUncropped.split("x").length===2)
					meta.image = { width : +r.meta.dimUncropped.split("x")[0], height : +r.meta.dimUncropped.split("x")[1] };
			}
		}

		return meta;
	}
}
