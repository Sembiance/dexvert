import {xu, fg} from "xu";
import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {imageUtil} from "xutil";
import {classifyImage} from "../classifyUtil.js";
import {programs} from "../program/programs.js";
import {identify} from "../identify.js";

// These particular kinds of images often look like noise/static/garbage and are usually caught by the classify garbage model
const CLASSIFY_PATH_EXCLUSIONS = [
	"texture", "textura",
	"background", "backgrnd",
	"repeatable",
	"stereo", "pattern", "noise", "illusion", "fractal", "border"
];

const MATCH_MAX_GARBAGE_PROBABILITIES = {
	magic    : 0.7,
	filename : 0.6,
	ext      : 0.6,
	fallback : 0.6,
	fileSize : 0.01
};

const UNSAFE_MAX_IMAGE_SIZE = 25000;
const SKIP_CLASSIFY_MAX_IMAGE_SIZE = 6000;

export class image extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {ids : identifications} = await identify(dexFile);
		const dexid = identifications.find(id => id.from==="dexvert" && id.family==="image");
		if(!dexid)
		{
			xlog.warn`DELETING OUTPUT due to not being identified as an image: ${dexFile.pretty()}`;
			return false;
		}

		const meta = {};
		// SVG's are VERY problematic for imagemagick to deal with. Loading up inkscape in the background and spinning at 100% CPU for ages while it renders some 65,000px wide SVG
		// So we don't even bother doing getImageInfo/identify and we just load up the file, parse as XML and deduce width/height from that
		// We can also check to make sure it actually has sub-elements and isn't just empty
		if(dexid.formatid==="svg")
			Object.assign(meta, (await Program.runProgram("svgInfo", dexFile, {xlog, autoUnlink : true})).meta);
		else
			Object.assign(meta, await imageUtil.getInfo(dexFile.absolute));

		if(!meta.width || !meta.height)
		{
			xlog.warn`Image failed verification due to no width (${meta.width}) or height (${meta.height})`;
			return false;
		}

		const isUnsafe = programs[dexState.ran?.at(-1)?.programid]?.unsafe || dexState.ran?.at(-1)?.unsafe;

		if(isUnsafe && meta.width===1 && meta.height===1)
		{
			xlog.warn`Image failed verification due to being unsafe with a 1x1 resulting image`;
			return false;
		}

		if(isUnsafe && meta.opaque && meta.colorCount<=1)
		{
			xlog.warn`Image failed verification due to being unsafe with an opaque result and 1 color`;
			return false;
		}

		if(isUnsafe && [meta.width, meta.height].some(v => v>=UNSAFE_MAX_IMAGE_SIZE))
		{
			if(meta.height>=UNSAFE_MAX_IMAGE_SIZE)
				dexState.imageFailedTooTall = true;
			xlog.warn`Image failed verification due to being unsafe with a width (${meta.width}) or height (${meta.height}) > ${UNSAFE_MAX_IMAGE_SIZE}`;
			return false;
		}

		if(dexid.formatid==="svg" && meta.colorCount<2 && !dexState.format.allow2ColorSVG)
		{
			xlog.warn`Image failed verification due to being unsafe an SVG with less than 2 colors.`;
			return false;
		}
		
		let skipClassify = !!dexState.format.skipClassify;

		// Only classify images if a program or format specified it specifically
		if(!skipClassify && !dexState.format.classify && !dexState.ran.some(r => programs[r.programid].classify))
			skipClassify = `Format ${dexState.format.formatid} and no ran programs require classification`;

		// Only classify these image types
		if(!skipClassify && !["gif", "png", "jpg", "webp", "svg"].includes(dexid.formatid))
			skipClassify = `Unsupported image formatid: ${dexid.formatid}`;
		
		// Don't classify if the full original absolute path or formatid includes any of these names as it will likely come back as a false positive as they tend to look like "noise"
		if(!skipClassify && CLASSIFY_PATH_EXCLUSIONS.some(v => dexid.formatid.toLowerCase().includes(v) || dexState.original.input.absolute.toLowerCase().includes(v)))
			skipClassify = `Contains a known 'noisy' pattern in original file path`;
		
		// Don't classify if the dimensions are too big
		if(!skipClassify && [meta.width, meta.height].some(v => v>=SKIP_CLASSIFY_MAX_IMAGE_SIZE))
			skipClassify = `Width or height is larger than ${SKIP_CLASSIFY_MAX_IMAGE_SIZE} : ${meta.width}x${meta.height}`;
		
		if(!skipClassify)
		{
			// classifyUtil.classifyImage will convert these into PNG before sending to the model
			const garbage = await classifyImage(dexFile.absolute, "garbage", xlog);
			if(typeof garbage!=="number" || garbage<0 || garbage>1)
				throw new Error(`Got invalid garabge result for ${dexFile.pretty()} ${dexState.original.input.pretty()} ${garbage}`);

			if((garbage || 0)>MATCH_MAX_GARBAGE_PROBABILITIES[dexState.id.matchType])
				return xlog.warn`Image failed verification due to being detected as ${fg.peach("garbage")} with val ${garbage} for: ${dexFile.pretty()} ${dexState.original.input.pretty()}`, false;

			xlog.debug`Image passed verification with garbage val ${garbage}`;
		}
		else
		{
			xlog.info`image.verify is ${fg.orange("SKIPPING")} classification: ${skipClassify}`;
		}

		return {identifications, meta};
	}

	// gets meta information for the given input and format
	async meta(inputFile, format, xlog)
	{
		if(!format.metaProvider)
			return;

		const meta = {};
		for(const metaProvider of format.metaProvider)
		{
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
			else if(metaProvider==="darkTable")
			{
				// camera images that darktable can identify
				const r = await Program.runProgram("darktable_rs_identify", inputFile, {xlog});
				if(r.meta?.dimUncropped && r.meta.dimUncropped.split("x").length===2)
					Object.assign(meta, { width : +r.meta.dimUncropped.split("x")[0], height : +r.meta.dimUncropped.split("x")[1] });
				await r.unlinkHomeOut();
			}
		}

		return meta;
	}
}
