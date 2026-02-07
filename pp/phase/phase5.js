import {xu} from "xu";
import {fileUtil} from "xutil";
import {C, classify} from "../ppUtil.js";
import {path} from "std";
import {AgentPool} from "AgentPool";

// Phase 5 - Any browser-safe images should be prepared and then checked for NSFW, OCR and should be vectorized
export default async function phase5({itemWebDirPath, itemThumbDirPath, itemFileDirPath, itemClassifyDirPath, itemClassifyTmpDirPath, taskRunner, xlog})
{
	const itemClassifyImageDirPath = path.join(itemClassifyDirPath, "image");
	await Deno.mkdir(itemClassifyImageDirPath, {recursive : true});

	taskRunner.startProgress(0, "Finding images for classification...");
	const folderPaths = await fileUtil.tree(itemWebDirPath, {nofile : true, sort : true, relative : true});
	folderPaths.unshift("");

	const images = [];
	await folderPaths.parallelMap(async folderPath =>
	{
		const jsonPaths = (await fileUtil.tree(path.join(itemWebDirPath, folderPath), {nodir : true, regex : /\.json$/i, sort : true, depth : 1, relative : true})).sortMulti(v => v.toLowerCase());
		taskRunner.setMax(taskRunner.max+jsonPaths.length);

		await jsonPaths.parallelMap(async jsonPath =>
		{
			const webFilePath = path.join(itemWebDirPath, folderPath, jsonPath);
			const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));

			if(!fileData.fileid)
				return taskRunner.increment();

			const imageBaseData = {itemClassifyTmpDirPath, itemClassifyImageDirPath, fileid : fileData.fileid, formatid : (fileData.content?.formatid || fileData.formatid)};
			if(C.BROWSER_FORMATS.image.includes(fileData.formatid))
				images.push({...imageBaseData, filePath : (fileData.content?.filePath || fileData.filePath), meta : fileData.meta || {}, liveOutput : xlog.atLeast("info")});
			else if(C.BROWSER_FORMATS.poly.includes(fileData.formatid))
				images.push({...imageBaseData, filePath : path.join(itemThumbDirPath, path.relative(itemFileDirPath, fileData.filePath)), meta : fileData.meta || {}, liveOutput : xlog.atLeast("info")});
			
			taskRunner.increment();
		});
	}, taskRunner.folderParallelism);
	
	if(!images.length)
		return taskRunner.phaseComplete();

	taskRunner.startProgress(images.length, "Preparing images for classification...");
	const filesToProcess = [];

	const onSuccess = data =>
	{
		if(data.error)
			taskRunner.addError(data.error);
		else
			filesToProcess.push(data);
		taskRunner.increment();
	};

	const prepareImagePool = new AgentPool(path.join(import.meta.dirname, "..", "prepareClassifyImage.agent.js"), {onSuccess, xlog});
	await prepareImagePool.init();
	await prepareImagePool.start();
	prepareImagePool.process(images);
	await xu.waitUntil(() => prepareImagePool.empty());
	await prepareImagePool.stop();

	if(!filesToProcess.length)
		return taskRunner.phaseComplete();

	// NSFW
	await classify({
		taskRunner, xlog, filesToProcess : filesToProcess.shuffle(), itemClassifyDirPath,
		filesDirPath : itemClassifyImageDirPath,
		type         : "nsfw",
		libraries    : ["tensorrt_libs", "tensorrt_bindings", "tensorrt", "nvidia/cudnn/lib", "nvidia/cuda_runtime/lib", "nvidia/cublas/lib", "torch/lib"],
		preProcess   : true,
		filesAtOnce  : 200,
		processor    : async (fileBatch, results) =>
		{
			for(const [i, nsfwScore] of Object.entries(results))
			{
				const webFilePath = path.join(itemWebDirPath, `${fileBatch[i].fileid}${C.UTFCHAR}.json`);
				const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));

				fileData.indexData.offensive ||= {};
				fileData.indexData.offensive.racy = Math.round(Math.min(nsfwScore, C.NSFW_RACY_MAX).scale(0, C.NSFW_RACY_MAX, 1, 5));
				fileData.indexData.offensive.adult = Math.round(nsfwScore.scale(0, 100, 1, 5));

				await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));

				const parentWebFilePath = path.join(itemWebDirPath, path.dirname(path.dirname(fileData.fileid)), `${path.basename(path.dirname(fileData.fileid))}${C.UTFCHAR}.json`);
				const parentFileData = await xu.tryFallbackAsync(async () => xu.parseJSON(await fileUtil.readTextFile(parentWebFilePath)));
				if(parentFileData?.content?.fileid && parentFileData?.content?.fileid===fileData.fileid)
				{
					parentFileData.indexData.offensive = Object.fromEntries(Object.entries(fileData.indexData.offensive));
					await fileUtil.writeTextFile(parentWebFilePath, JSON.stringify(parentFileData));
				}
			}
		}
	});

	// OCR
	const ocrToRetry = [];
	const ocrProcessor = async (fileBatch, results) =>
	{
		for(const [i, ocrData] of Object.entries(results))
		{
			if(ocrData.err)
			{
				// retry each file ONCE
				if(!fileBatch[i].failedOnce)
				{
					fileBatch[i].failedOnce = true;
					ocrToRetry.push(fileBatch[i]);
				}
				else
				{
					taskRunner.addError(`OCR error for ${fileBatch[i].fileid}: ${ocrData.err}`);
				}
				continue;
			}
				
			if(ocrData.pages.length>1)
			{
				taskRunner.addError(`${fileBatch[i]} has more than 1 page, never seen this before, UNHANDLED!`);
				continue;
			}

			const page = ocrData.pages[0];
			if(!page.blocks.length)
				continue;

			const textBoxes = [];
			for(const block of page.blocks)
			{
				for(const line of block.lines)
				{
					for(const word of line.words)
					{
						const minY = word.geometry[0][1]*page.dimensions[0];
						const maxY = word.geometry[1][1]*page.dimensions[0];
						const boxH = maxY-minY;
						const midY = [minY, maxY].average();

						const minX = word.geometry[0][0]*page.dimensions[1];
						const maxX = word.geometry[1][0]*page.dimensions[1];
						const boxW = maxX-minX;
						const midX = [minX, maxX].average();

						textBoxes.push({text : word.value, minY, maxY, boxH, midY, minX, maxX, boxW, midX});
					}
				}
			}

			let rows = [];
			for(const textBox of textBoxes)
			{
				const sameLine = rows.find(cols => cols.some(col => textBox.midY>=col.minY && textBox.midY<=col.maxY));
				if(sameLine)
					sameLine.push(textBox);
				else
					rows.push([textBox]);
			}

			rows = rows.sortMulti([cols => cols.map(({midY}) => midY).average()], [false]);
			const ocrTexts = [];
			for(const cols of rows)
				ocrTexts.push(cols.sortMulti([({midX}) => midX], [false]).map(({text}) => text).join(" "));

			const ocrText = ocrTexts.join(" ").innerTrim().trim();
			if(!ocrText.length)
				continue;
		
			const webFilePath = path.join(itemWebDirPath, `${fileBatch[i].fileid}${C.UTFCHAR}.json`);
			const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));
			if(!fileData?.indexData)
			{
				taskRunner.addError(`Failed to parse fileData for ${fileBatch[i].fileid} at location: ${webFilePath}`);
				continue;
			}

			fileData.indexData.ocrText = ocrText;

			await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));

			const parentWebFilePath = path.join(itemWebDirPath, path.dirname(path.dirname(fileData.fileid)), `${path.basename(path.dirname(fileData.fileid))}${C.UTFCHAR}.json`);
			const parentFileData = await xu.tryFallbackAsync(async () => xu.parseJSON(await fileUtil.readTextFile(parentWebFilePath)));
			if(parentFileData?.content?.fileid && parentFileData?.content?.fileid===fileData.fileid)
			{
				parentFileData.indexData.ocrText = ocrText;
				await fileUtil.writeTextFile(parentWebFilePath, JSON.stringify(parentFileData));
			}
		}
	};

	const ocrOptions = {
		taskRunner, xlog, itemClassifyDirPath,
		filesDirPath     : itemClassifyImageDirPath,
		type             : "ocr",
		libraries        : ["tensorrt_libs", "tensorrt_bindings", "tensorrt", "nvidia/cuda_runtime/lib"],
		preProcess       : true,
		preProcessSuffix : ".npy",
		batchSize        : 16,
		filesAtOnce      : 200,
		processor        : ocrProcessor
	};

	await classify({...ocrOptions, filesToProcess : filesToProcess.sortMulti([o => o.pixelCount], [true])});
	
	// we retry failed OCR files once, because sometimes the OCR fails with: Tensor's shape (1, 30, 203, 3) is not compatible with supplied shape [1, 32, 128, 3]
	if(ocrToRetry.length)
		await classify({...ocrOptions, filesToProcess : ocrToRetry});

	// vectorizeImage
	await classify({
		taskRunner, xlog, filesToProcess : filesToProcess.shuffle(), itemClassifyDirPath,
		filesDirPath : itemClassifyImageDirPath,
		type         : "vectorizeImage",
		libraries    : ["nvidia/cudnn/lib", "nvidia/cuda_runtime/lib", "nvidia/cublas/lib", "torch/lib"],
		preProcess   : true,
		filesAtOnce  : 100,
		processor    : async (fileBatch, results) =>
		{
			for(const [i, vectors] of Object.entries(results))
			{
				if(vectors.length!==C.SEARCH_VISUAL_VECTOR_LENGTH)
					continue;

				const webFilePath = path.join(itemWebDirPath, `${fileBatch[i].fileid}${C.UTFCHAR}.json`);
				const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));
				if(!fileData)
				{
					taskRunner.addError(`Failed to parse fileData for ${fileBatch[i].fileid} at location: ${webFilePath}`);
					continue;
				}

				fileData.indexData.v = vectors;

				await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));

				const parentWebFilePath = path.join(itemWebDirPath, path.dirname(path.dirname(fileData.fileid)), `${path.basename(path.dirname(fileData.fileid))}${C.UTFCHAR}.json`);
				const parentFileData = await xu.tryFallbackAsync(async () => xu.parseJSON(await fileUtil.readTextFile(parentWebFilePath)));
				if(parentFileData?.content?.fileid && parentFileData?.content?.fileid===fileData.fileid)
				{
					parentFileData.indexData.v = Array.from(fileData.indexData.v);
					await fileUtil.writeTextFile(parentWebFilePath, JSON.stringify(parentFileData));
				}
			}
		}
	});

	await fileUtil.unlink(itemClassifyImageDirPath, {recursive : true});

	taskRunner.phaseComplete();
}
