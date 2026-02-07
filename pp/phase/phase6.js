import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";
import {C, classify} from "../ppUtil.js";

// Phase 6 - Any browser-safe audio/video should be prepared and then processed with transcription to get text content
export default async function phase6({itemWebDirPath, itemClassifyDirPath, taskRunner, xlog})
{
	const itemClassifyAudioDirPath = path.join(itemClassifyDirPath, "audio");
	await Deno.mkdir(itemClassifyAudioDirPath, {recursive : true});

	const filesToPreProcess = [];

	taskRunner.startProgress(0, "Finding audio/video files for transcription...");
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

			if(!fileData.fileid || !["mp3", "mp4"].includes(fileData.formatid))
				return taskRunner.increment();

			filesToPreProcess.push({filePath : fileData.filePath, fileid : fileData.fileid});
			
			taskRunner.increment();
		});
	}, taskRunner.folderParallelism);

	if(!filesToPreProcess.length)
		return taskRunner.phaseComplete();

	// Pre-process and keep only those that have audio
	taskRunner.startProgress(filesToPreProcess.length, "Preparing audio files for transcription...");
	const filesToProcess = [];
	await filesToPreProcess.parallelMap(async fileToPreProcess =>
	{
		const filePath = await fileUtil.genTempPath(itemClassifyAudioDirPath, ".mp3");	// important: we need a filename without spaces, which luckily we get from genTempPath
		await runUtil.run("ffmpeg", ["-y", "-threads", "1", "-i", `file:${fileToPreProcess.filePath}`, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", "-bitexact", "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact", filePath]);
		
		if(await fileUtil.exists(filePath))	// We don't log an error here because it's pretty common for videos to not have audio
			filesToProcess.push({filePath, fileid : fileToPreProcess.fileid});

		taskRunner.increment();
	}, navigator.hardwareConcurrency);

	if(!filesToProcess.length)
		return taskRunner.phaseComplete();

	// transcribe
	await classify({
		taskRunner, xlog, filesToProcess  : filesToProcess.shuffle(), itemClassifyDirPath,
		filesDirPath   : itemClassifyAudioDirPath,
		type           : "transcribe",
		libraries      : ["tensorrt", "nvidia/cudnn/lib", "nvidia/cuda_runtime/lib", "nvidia/cublas/lib", "torch/lib"],
		processTimeout : xu.MINUTE*25,
		filesAtOnce    : 50,
		processor      : async (fileBatch, results) =>
		{
			for(const [i, transcribeData] of Object.entries(results))
			{
				if(transcribeData.err)
				{
					taskRunner.addError(`Transcription error for ${fileBatch[i].fileid}: ${transcribeData.err}`);
					continue;
				}

				let transcriptionText = (transcribeData || []).sortMulti([o => o.start_time]).map(o => (o.text || "").trim()).join(" ").innerTrim().trim();

				// Remove common hallucinations
				const hallucinations = [/\. \./i, /thank you for watching!/gi, /thanks for watching!/gi, /(\s*\b(you|the|i)\b\s*){2}/gi, /^\.?\s*(you|the|i|\.)\s*\.?$/i];
				for(const hallucination of hallucinations)
				{
					while(hallucination.test(transcriptionText))
					{
						transcriptionText = transcriptionText.replace(hallucination, "");
						transcriptionText = transcriptionText.innerTrim().trim();
					}
				}
				if(!transcriptionText.length)
					continue;

				const webFilePath = path.join(itemWebDirPath, `${fileBatch[i].fileid}${C.UTFCHAR}.json`);
				const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));

				fileData.indexData.transcriptionText = transcriptionText;

				await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));

				const parentWebFilePath = path.join(itemWebDirPath, path.dirname(path.dirname(fileData.fileid)), `${path.basename(path.dirname(fileData.fileid))}${C.UTFCHAR}.json`);
				const parentFileData = await xu.tryFallbackAsync(async () => xu.parseJSON(await fileUtil.readTextFile(parentWebFilePath)));
				if(parentFileData?.content?.fileid && parentFileData?.content?.fileid===fileData.fileid)
				{
					parentFileData.indexData.transcriptionText = transcriptionText;
					await fileUtil.writeTextFile(parentWebFilePath, JSON.stringify(parentFileData));
				}
			}
		}
	});
	
	await fileUtil.unlink(itemClassifyAudioDirPath, {recursive : true});

	taskRunner.phaseComplete();
}
