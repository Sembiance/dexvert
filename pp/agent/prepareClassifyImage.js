import {xu} from "xu";
import {agentInit} from "AgentPool";
import {fileUtil, runUtil, imageUtil} from "xutil";
import {C} from "../ppUtil.js";

await agentInit(async image =>
{
	// convert is super sensitive to filenames so we symlink to it
	// we choose the image format as the extension (only possible options are C.BROWSER_FORMATS.image) to prevent imagemagick from deducing file type from extension (such as a gif file ending in .map)
	let safeFilePath = await fileUtil.genTempPath(image.itemClassifyTmpDirPath, `.${image.formatid}`);
	
	await Deno.symlink(image.filePath, safeFilePath);

	// inkscape is PAINFULLY slow at rendering SVGs. ImageMagick's convert just uses inkscape. So let's convert using resvg instead which is fast
	if(image.formatid==="svg")
	{
		const tmpPNGFilePath = await fileUtil.genTempPath(image.itemClassifyTmpDirPath, ".png");
		const resvgArgs = [];
		resvgArgs.push((image.meta?.height || 0)>(image.meta?.width || 0) ? "--height" : "--width");
		resvgArgs.push("500", safeFilePath, tmpPNGFilePath);
		const {stderr : resvgErr} = await runUtil.run("resvg", resvgArgs, {timeout : xu.MINUTE*2});
		await fileUtil.unlink(safeFilePath);
		if(!await fileUtil.exists(tmpPNGFilePath))
			return {error : `resvg failed for ${image.fileid} with stderr: ${resvgErr}`};

		safeFilePath = tmpPNGFilePath;
	}

	// now that we have a safely named PNG source, we need to scale it up or down so that OCR and NSFW works better
	const filePath = await fileUtil.genTempPath(image.itemClassifyImageDirPath, ".png");

	const convertArgs = [...C.CONVERT_PNG_ARGS, `${safeFilePath}[${image.frameNum || 0}]`];	// ensure if it's animated or has multiple layers, we just get a single frame
	convertArgs.push("-filter", "point");	// ensure scaled up images are not blurry
	convertArgs.push("-auto-orient");	// honor EXIF orientation
	convertArgs.push("-resize", `${C.CLASSIFY_IMAGE_DIM_MAX}>`);	// will scale image down BEFORE scaling up, this ensures we don't scale up past the 100,000 policy.xml limit (since 1500*50 is only 75,000 pixels)
	convertArgs.push("-resize", `${C.CLASSIFY_IMAGE_DIM_MIN}^<`);	// will scale image up to at least this resolution
	convertArgs.push("-resize", `${C.CLASSIFY_IMAGE_DIM_MAX}>`);	// will scale image down to at most this resolution
	convertArgs.push("-strip");		// remove metadata
	convertArgs.push(filePath);

	const {stderr : convertResize1} = await runUtil.run("magick", convertArgs, {timeout : xu.MINUTE*5, signal : "SIGKILL"});
	await fileUtil.unlink(safeFilePath);

	if(!await fileUtil.exists(filePath))
		return {error : `convert resize #1 failed for ${image.fileid} with stderr: ${convertResize1}`};

	let widthHeightErr = null;
	const [imageWidth, imageHeight] = (await imageUtil.getWidthHeight(filePath).catch(err => { widthHeightErr = err; }) || [null, null]);
	if(widthHeightErr || !imageWidth || !imageHeight || isNaN(imageWidth) || isNaN(imageHeight))
	{
		await fileUtil.unlink(filePath);
		return {error : `Invalid WxH ${imageWidth}x${imageHeight} with err ${widthHeightErr}`};
	}

	return {filePath, fileid : image.fileid, pixelCount : imageWidth*imageHeight};
});
