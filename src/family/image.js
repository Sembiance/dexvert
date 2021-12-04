import {xu, fg} from "xu";
import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {imageUtil} from "xutil";
import {initDOMParser, DOMParser} from "denoLandX";
import {path} from "std";
import {programs} from "../program/programs.js";

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

const UNSAFE_MAX_IMAGE_SIZE = 25000;
const SKIP_TENSOR_MAX_IMAGE_SIZE = 6000;

const GARBAGE_DETECTED_DIR_PATH = "/mnt/dexvert/garbageDetected";

export class image extends Family
{
	metaids = ["image", "darkTable", "ansiArt", ...Object.keys(programs)];

	async verify(dexState, dexFile, identifications)
	{
		const xlog = dexState.xlog;
		const dexid = identifications.find(id => id.from==="dexvert" && id.family==="image");
		if(!dexid)
		{
			xlog.warn`DELETING OUTPUT due to not being identified as an image: ${dexFile.pretty()}`;
			return false;
		}

		const meta = {};
		// SVG's are VERY problematic for imagemagick to deal with. Loading up inkscape in the background and spinning at 100% CPU for ages while it renders some 65,000px wide SVG
		// So we don't even bother doing getImageInfo/identify and we just load up the file, parse as XML and deduce width/height from that
		// We can also check to make sure it actually has sub-elements, sometimes totalCADConverterX for example will produce an empty <svg></svg> file (NUTBOLT.DWG)
		if(dexid.formatid==="svg")
		{
			const r = await Program.runProgram("svgInfo", dexFile, {xlog});
			Object.assign(meta, r.meta);
			await r.unlinkHomeOut();
		}
		else
		{
			Object.assign(meta, await imageUtil.getInfo(dexFile.absolute));
		}

		if(!meta.width || !meta.height)
		{
			xlog.warn`Image failed verification due to no width (${meta.width}) or height (${meta.height})`;
			return false;
		}
		
		const isUnsafe = programs[dexState.ran.at(-1).programid].unsafe || dexState.ran.at(-1).unsafe;

		if(isUnsafe && meta.opaque && meta.colorCount<=1)
		{
			xlog.warn`Image failed verification due to being unsafe with an opaque result and 1 color`;
			return false;
		}

		if(isUnsafe && [meta.width, meta.height].some(v => v>=UNSAFE_MAX_IMAGE_SIZE))
		{
			xlog.warn`Image failed verification due to being unsafe with a width (${meta.width}) or height (${meta.height}) > ${UNSAFE_MAX_IMAGE_SIZE}`;
			return false;
		}

		if(dexid.formatid==="svg" && meta.colorCount<2)
		{
			xlog.warn`Image failed verification due to being unsafe an SVG with less than 2 colors.`;
			return false;
		}
		
		let skipTensor = null;

		// Only classify these image types
		if(!["gif", "png", "jpg", "webp", "svg"].includes(dexid.formatid))
			skipTensor = `Unsupported image formatid: ${dexid.formatid}`;
		
		// Don't classify if the full original absolute path or formatid includes any of these names as it will likely come back as a false positive as they tend to look like "noise"
		if(TENSOR_PATH_EXCLUSIONS.some(v => dexid.formatid.toLowerCase().includes(v) || dexState.original.input.absolute.toLowerCase().includes(v)))
			skipTensor = `Contains a known 'noisy' pattern in original file path`;
		
		// Don't classify if the dimensions are too big
		if([meta.width, meta.height].some(v => v>=SKIP_TENSOR_MAX_IMAGE_SIZE))
			skipTensor = `Width or height is larger than ${SKIP_TENSOR_MAX_IMAGE_SIZE} : ${meta.width}x${meta.height}`;
		
		if(!skipTensor)
		{
			// loaded dynamically because tensorUtil requires identify which requires formats and this is a family, anyways, circular dependency seen in util/buildFormats.js
			const {classifyImage} = await import("../tensorUtil.js");

			// tensorUtil.classifyImage will convert these into PNG before sending to the tensor
			const garbage = await classifyImage(dexFile.absolute, "garbage");
			if(typeof garbage!=="number" || garbage<0 || garbage>1)
				throw new Error(`Got invalid garabge result for ${dexFile.pretty()} ${dexState.original.input.pretty()} ${garbage}`);

			if((garbage || 0)>MATCH_MAX_GARBAGE_PROBABILITIES[dexState.id.matchType])
			{
				xlog.warn`Image failed verification due to being detected as ${fg.peach("garbage")} with val ${garbage} for: ${dexFile.pretty()} ${dexState.original.input.pretty()}`;
				await Deno.copyFile(dexFile.absolute, path.join(GARBAGE_DETECTED_DIR_PATH, `${garbage.noExponents()}-${Math.randomInt(1, 10000)}-${dexState.format.formatid}-${dexState.original.input.absolute.replaceAll("/", ":")}-${dexFile.rel.replaceAll("/", ":")}`));
				return false;
			}
		}
		else
		{
			xlog.warn`image.verify is ${fg.orange("SKIPPING")} garbage classification: ${skipTensor}`;
		}

		if(dexState.phase?.format?.verify && !dexState.phase.format.verify({dexState, dexFile, identifications, meta}))
		{
			xlog.info`Image failed format.verify() call`;
			return false;
		}

		return true;
	}

	// gets meta information for the given input and format
	async meta(inputFile, format, xlog)
	{
		if(!format.metaProvider)
			return;

		const meta = {};
		for(const metaProvider of format.metaProvider)
		{
			xlog.info`Getting meta from provider ${metaProvider}`;

			// imageMagick meta provider
			if(metaProvider==="image")
			{
				const info = await imageUtil.getInfo(inputFile.absolute);
				if(info.err)
				{
					xlog.warn`imageUtil.getInfo() returned an err ${info.err}`;
					delete info.err;
				}
				delete info.size;
				Object.assign(meta, info);
			}
			else if(metaProvider==="ansiArt")
			{
				// ansiArt, we convert with deark to html and then parse the HTML for meta info about the ansi art file
				const r = await Program.runProgram("deark", inputFile, {flags : {charOutType : "html"}, xlog});
				if(r.f.new)
				{
					const htmlRaw = await Deno.readTextFile(r.f.new.absolute);
					await initDOMParser();
					const doc = new DOMParser().parseFromString(htmlRaw, "text/html");
					Array.from(doc.querySelectorAll("table.htt td.htc")).forEach(metaCell =>
					{
						const key = (metaCell.querySelector("span.hn") || {textContent : ""}).textContent.trim().trimChars(":");
						const val = (metaCell.querySelector("span.hv") || {textContent : ""}).textContent.trim().trimChars(":");
						if(key && val && key.length>0 && val.length>0)
							meta[key.toLowerCase()] = val;
					});
				}
				await r.unlinkHomeOut();
			}
			else if(metaProvider==="darkTable")
			{
				// camera images that darktable can identify
				const r = await Program.runProgram("darktable_rs_identify", inputFile, {xlog});
				if(r.meta?.dimUncropped && r.meta.dimUncropped.split("x").length===2)
					Object.assign(meta, { width : +r.meta.dimUncropped.split("x")[0], height : +r.meta.dimUncropped.split("x")[1] });
				await r.unlinkHomeOut();
			}
			else
			{
				// if none of the above, we assume it's a program
				const r = await Program.runProgram(metaProvider, inputFile, {xlog});
				if(r.meta)
					Object.assign(meta, r.meta);
				await r.unlinkHomeOut();
			}
		}

		return meta;
	}
}
