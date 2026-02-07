import {xu} from "xu";
import {agentInit} from "AgentPool";
import {path} from "std";
import {fileUtil, runUtil} from "xutil";
import {C} from "../ppUtil.js";

await agentInit(async ({dexid, meta, filePath, content, itemWebDirPath, itemFileDirPath, itemThumbDirPath}) =>
{
	const thumbFilePath = path.join(itemThumbDirPath, path.relative(itemFileDirPath, filePath));
	await Deno.mkdir(path.dirname(thumbFilePath), {recursive : true});

	let tmpImagePath = null;

	let thumbWidth = C.BROWSE_THUMB_WIDTH;
	let thumbHeight = C.BROWSE_THUMB_HEIGHT;

	const parentFileData = xu.parseJSON(await xu.tryFallbackAsync(async () => await fileUtil.readTextFile(path.join(itemWebDirPath, `${path.relative(itemFileDirPath, path.dirname(filePath))}${C.UTFCHAR}.json`))));
	if(parentFileData?.dexid?.family==="font")
	{
		thumbWidth = C.BROWSE_FONT_THUMB_WIDTH;
		thumbHeight = C.BROWSE_FONT_THUMB_HEIGHT;
	}

	if(C.BROWSER_FORMATS.video.includes(dexid.formatid))
	{
		thumbWidth = C.BROWSE_VIDEO_THUMB_WIDTH;
		thumbHeight = C.BROWSE_VIDEO_THUMB_HEIGHT;
	}

	const RUN_OPTIONS = {timeout : xu.MINUTE*2, timeoutSignal : "SIGKILL"};

	async function buildThumb()
	{
		let stdout, stderr;
		if(C.BROWSER_FORMATS.video.includes(dexid.formatid))
		{
			// sometimes ffmpeg is sensitive regarding the output file path, so we use a tmp file and then rename it to the final path
			tmpImagePath = await fileUtil.genTempPath(undefined, ".png");

			// grab a thumbnail for the video so we can show it as a placeholder poster for video elements
			({stdout, stderr} = await runUtil.run("ffmpeg", ["-i", `file:${filePath}`, "-frames:v", "1", "-an", "-s", `${thumbWidth}x${thumbHeight}`, "-ss", "0", "-update", "true", "-f", "image2", "-c", "png", `file:${tmpImagePath}`], RUN_OPTIONS));
			await fileUtil.move(tmpImagePath, thumbFilePath);
			tmpImagePath = null;
		}
		else if(C.BROWSER_FORMATS.poly.includes(dexid.formatid))
		{
			await xu.waitUntil(async () =>
			{
				const lockFile = await fileUtil.lock(C.POLY_THUMB_COUNT_LOCK_FILE_PATH);
				let activePolyCount = +((await fileUtil.readTextFile(C.POLY_THUMB_COUNT_FILE_PATH)) || "0").trim();
				if(activePolyCount>=C.MAX_POLY_THUMB_ACTIVE)
				{
					await fileUtil.unlock(lockFile);
					return false;
				}

				activePolyCount++;
				await fileUtil.writeTextFile(C.POLY_THUMB_COUNT_FILE_PATH, activePolyCount.toString());
				await fileUtil.unlock(lockFile);
				return true;
			});
			({stdout, stderr} = await runUtil.run("deno", runUtil.denoArgs(path.join(import.meta.dirname, "..", "poly2thumb.js"), `--tmpDirPath=${C.POLY_TMP_DIR}`, filePath, thumbFilePath), runUtil.denoRunOpts({timeout : xu.MINUTE*30})));
			if(!await fileUtil.exists(thumbFilePath))
				({stdout, stderr} = await runUtil.run("deno", runUtil.denoArgs(path.join(import.meta.dirname, "..", "poly2thumbStatic.js"), `--tmpDirPath=${C.POLY_TMP_DIR}`, filePath, thumbFilePath), runUtil.denoRunOpts({timeout : xu.MINUTE*5})));

			const lockFile = await fileUtil.lock(C.POLY_THUMB_COUNT_LOCK_FILE_PATH);
			let activePolyCount = +((await fileUtil.readTextFile(C.POLY_THUMB_COUNT_FILE_PATH)) || "0").trim();
			activePolyCount--;
			await fileUtil.writeTextFile(C.POLY_THUMB_COUNT_FILE_PATH, activePolyCount.toString());
			await fileUtil.unlock(lockFile);
		}
		else
		{
			// svg files take forever to render with imagemagick, so we use resvg to render them to a tmpImagePath
			// since we don't know whether the resulting PNG will be larger than our target thumb, we still will resize the PNG with imagemagick to make smaller, if needed
			if(dexid.formatid==="svg")
			{
				tmpImagePath = await fileUtil.genTempPath(undefined, ".png");
				const resvgArgs = [];
				if((meta?.height || 0)>(meta?.width || 0))
					resvgArgs.push("--height", thumbHeight.toString());
				else
					resvgArgs.push("--width", thumbWidth.toString());
				resvgArgs.push(filePath, tmpImagePath);
				({stdout, stderr} = await runUtil.run("resvg", resvgArgs, RUN_OPTIONS));
			}
			else
			{
				// ensure the extension matches the image type, to ensure convert will properly make a thumb
				tmpImagePath = await fileUtil.genTempPath(undefined, `.${dexid.formatid}`);
				await Deno.symlink(filePath, tmpImagePath);
			}

			// convert messes up some filenames in the output, even though I specify -define filename:literal=true ()
			if(await fileUtil.exists(tmpImagePath))
			{
				const safeOutImagePath = await fileUtil.genTempPath(undefined, ".gif");
				if(meta?.animated && ["gif", "webp"].includes(dexid.formatid))
				{
					// I could convert .webp animated files to WEBP output, but GIF is small enough at thumbnail size and is more compatible with older browsers, so "just choose GIF" (tm)
					// Coalesce will ensure all frames are the full size of the image before resizing and then deconstruct will reduce frames down to their minimum size neded which saves on file size
					({stdout, stderr} = await runUtil.run("magick", [...C.CONVERT_ARGS, tmpImagePath, "-coalesce", "-resize", `${thumbWidth}x${thumbHeight}>`, "-deconstruct", `GIF:${safeOutImagePath}`], RUN_OPTIONS));

					// sometimes the conversion to animated GIF fails, so if we are missing our destination image, run again but with just one frame
					if(!await fileUtil.exists(safeOutImagePath) || !(await Deno.lstat(safeOutImagePath))?.size)
						({stdout, stderr} = await runUtil.run("magick", [...C.CONVERT_ARGS, `${tmpImagePath}[0]`, "-resize", `${thumbWidth}x${thumbHeight}>`, `GIF:${safeOutImagePath}`], RUN_OPTIONS));
				}
				else
				{
					// font previews are always PNG and we should just crop to top left for a nice big preview
					if(parentFileData?.dexid?.family==="font")
						({stdout, stderr} = await runUtil.run("magick", [...C.CONVERT_PNG_ARGS, `${tmpImagePath}[0]`, "-crop", `${thumbWidth}x${thumbHeight}+0+0`, `PNG:${safeOutImagePath}`], RUN_OPTIONS));
					else
						({stdout, stderr} = await runUtil.run("magick", [...C.CONVERT_PNG_ARGS, `${tmpImagePath}[0]`, "-auto-orient", "-resize", `${thumbWidth}x${thumbHeight}>`, `PNG:${safeOutImagePath}`], RUN_OPTIONS));
				}

				await fileUtil.move(safeOutImagePath, thumbFilePath);
			}
		}

		if(tmpImagePath)
			await fileUtil.unlink(tmpImagePath);

		// if we didn't produce the thumb file, show an error (unless our contentTwig isn't the same as this twig, which means a corrupted GIF was converted into a PNG and a thumb for this doesn't matter)
		const result = {};
		if(!await fileUtil.exists(thumbFilePath) && !content?.filePath)
		{
			result.error = `buildThumb failed [${path.relative(itemFileDirPath, filePath)}] ${`${stdout?.trim()} ${stderr?.trim()}`.trim()}${!await fileUtil.exists(filePath) ? " original DOES NOT EXIST!" : ""}`;
			await Deno.copyFile(C.BROKEN_IMAGE_FILE_PATH, thumbFilePath);
		}

		return result;
	}

	return await buildThumb();
});
