import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";
import {classify} from "../ppUtil.js";
import {C} from "../../src/C.js";

// Phase 7 - Any browser-safe audio should be processed with vectorization for auditory simularity search
export default async function phase7({itemWebDirPath, itemClassifyDirPath, taskRunner, xlog})
{
	const itemClassifyAudioDirPath = path.join(itemClassifyDirPath, "audioVectorize");
	await Deno.mkdir(itemClassifyAudioDirPath, {recursive : true});

	const filesToProcess = [];

	taskRunner.startProgress(0, "Finding audio files for vectorization...");
	const folderPaths = await fileUtil.tree(itemWebDirPath, {nofile : true, sort : true, relative : true});
	folderPaths.unshift("");
	await folderPaths.parallelMap(async folderPath =>
	{
		const jsonPaths = (await fileUtil.tree(path.join(itemWebDirPath, folderPath), {nodir : true, regex : /\.json$/i, sort : true, depth : 1, relative : true})).sortMulti(v => v.toLowerCase());
		taskRunner.setMax(taskRunner.max+jsonPaths.length);

		await jsonPaths.parallelMap(async jsonPath =>
		{
			const webFilePath = path.join(itemWebDirPath, folderPath, jsonPath);
			const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));

			if(!fileData.fileid || fileData.formatid!=="mp3")
				return taskRunner.increment();

			const filePath = await fileUtil.genTempPath(itemClassifyAudioDirPath, ".mp3");
			await Deno.copyFile(fileData.filePath, filePath);	// We need a filename without spaces, which we get from genTempPath
			filesToProcess.push({filePath, fileid : fileData.fileid});
			
			taskRunner.increment();
		});
	}, taskRunner.folderParallelism);

	if(!filesToProcess.length)
		return taskRunner.phaseComplete();

	// vectorizeAudio
	await classify({
		taskRunner, xlog, filesToProcess : filesToProcess.shuffle(), itemClassifyDirPath,
		filesDirPath : itemClassifyAudioDirPath,
		type         : "vectorizeAudio",
		libraries    : ["nvidia/cudnn/lib", "nvidia/cuda_runtime/lib", "nvidia/cublas/lib", "torch/lib", "torchaudio/lib"],
		preProcess   : true,
		filesAtOnce  : 100,
		processor    : async (fileBatch, results) =>
		{
			for(const [i, vectors] of Object.entries(results))
			{
				if(vectors.length!==C.SEARCH_AUDITORY_VECTOR_LENGTH)
					continue;

				const webFilePath = path.join(itemWebDirPath, `${fileBatch[i].fileid}${C.UTFCHAR}.json`);
				const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));

				fileData.indexData.va = vectors;

				await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));

				const parentWebFilePath = path.join(itemWebDirPath, path.dirname(path.dirname(fileData.fileid)), `${path.basename(path.dirname(fileData.fileid))}${C.UTFCHAR}.json`);
				const parentFileData = await xu.tryFallbackAsync(async () => xu.parseJSON(await fileUtil.readTextFile(parentWebFilePath)));
				if(parentFileData?.content?.fileid && parentFileData?.content?.fileid===fileData.fileid)
				{
					parentFileData.indexData.va = Array.from(fileData.indexData.va);
					await fileUtil.writeTextFile(parentWebFilePath, JSON.stringify(parentFileData));
				}
			}
		}
	});
	
	await fileUtil.unlink(itemClassifyAudioDirPath, {recursive : true});

	taskRunner.phaseComplete();
}
