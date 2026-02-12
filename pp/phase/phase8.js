/* eslint-disable no-loop-func */
import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import {C} from "../../src/C.js";
import {path} from "std";

const MAX_LINES_BYTES_WAIT_THRESHOLD = xu.MB*500;
const MAX_LINES_BYTES_RESUME_THRESHOLD = xu.MB*100;

// some index data is also needed in fileData for the web UI, so we copy it over here
function transferIndexDataToFileData(item, indexData, fileData)
{
	// copy our ocrText/transcriptionText into fileData for the view page and append to indexData.textContent for indexing
	if(indexData.ocrText)
		fileData.ocrText = indexData.ocrText;
	if(indexData.transcriptionText)
		fileData.transcriptionText = indexData.transcriptionText;

	// copy our offensive ratings into fileData for the view-image page and set the indexData.nsfw value accordingly
	if(indexData.offensive)
	{
		fileData.offensive = Object.fromEntries(Object.entries(indexData.offensive));

		// if we are an image or video on an item marked as NSFW, then we start off at NSFW classification level 1 rather than 0
		indexData.nsfw = item.nsfw && ["image", "video"].includes(fileData.family) ? 1 : 0;

		["adult", "racy"].forEach(type =>
		{
			if((fileData.offensive[type] || 0)>=C.OFFENSIVE_CONFIDENCE.LIKELY)
				indexData.nsfw+=(type==="adult" ? 2 : 1);	// nsfw is increased by 2 if the image is adult, 1 if racy
		});
	}
}

// Phase 8 - Create our .JSONL files for indexing
export default async function phase8({item, itemDirPath, itemWebDirPath, taskRunner, reportFilePath})
{
	const indexFilePath = path.join(itemDirPath, `${item.itemid}.jsonl`);

	// Otherwise we need to create an index file based on the fileData.indexData created in phase 4/5/6
	let indexedCount = 0;
	const indexFile = await Deno.open(indexFilePath, {create : true, write : true, truncate : true});
	const encoder = new TextEncoder();

	const lines = [];
	let linesByteUsage = 0;
	let finishedFindingLines = false;
	const lineIndexer = async function lineIndexer()
	{
		while(!finishedFindingLines || lines.length)	// eslint-disable-line no-unmodified-loop-condition
		{
			await xu.waitUntil(() => lines.length || finishedFindingLines);
			if(!lines.length && finishedFindingLines)
				return;

			const line = lines.pop();	// we use .pop() for performance vs .shift() because line order doesn't matter
			linesByteUsage-=line.length;
			await new Blob([encoder.encode(line + "\n")]).stream().pipeTo(indexFile.writable, {preventClose : true});	// eslint-disable-line prefer-template
			indexedCount++;
		}
	};
	const activeLineIndexer = lineIndexer();

	taskRunner.startProgress(0, "Generating .JSONL index files...");
	const folderPaths = await fileUtil.tree(itemWebDirPath, {nofile : true, sort : true, relative : true});
	folderPaths.unshift("");
	for(const folderPath of folderPaths)
	{
		const jsonPaths = (await fileUtil.tree(path.join(itemWebDirPath, folderPath), {nodir : true, regex : /\.json$/i, sort : true, depth : 1, relative : true})).sortMulti(v => v.toLowerCase());
		taskRunner.setMax(taskRunner.max+jsonPaths.length);

		await jsonPaths.parallelMap(async jsonPath =>
		{
			const webFilePath = path.join(itemWebDirPath, folderPath, jsonPath);
			const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));
			const indexData = fileData.indexData;
			if(!indexData)
				return taskRunner.increment();

			if(fileData.fileid)
			{
				// This has the side effect of making the parent items not longer searchable either, which isn't what we want
				// Since we can't actually get the file data out from the search engine and since the web UI will block access to the file both viewing and downloading, it's safe to just let blocked files be indexed
				//if(fileData.blocked)
				//	return taskRunner.increment();

				// We skip indexing any files that have a parent file whose content points to us, as we will index the parent 'original' file instead of this one
				const parentFileData = await xu.tryFallbackAsync(async () => xu.parseJSON(await fileUtil.readTextFile(path.join(itemWebDirPath, path.dirname(path.dirname(fileData.fileid)), `${path.basename(path.dirname(fileData.fileid))}${C.UTFCHAR}.json`))));
				if(parentFileData?.content?.fileid && parentFileData?.content?.fileid===fileData.fileid)
					return taskRunner.increment();
			}

			transferIndexDataToFileData(item, indexData, fileData);

			// Confirm we only have keys that we want to index
			const invalidKeys = Object.keys(indexData).subtractOnce([...Object.keys(C.SEARCH_SCHEMA), ...C.EXTRA_INDEX_KEYS]);
			if(invalidKeys.length)
				taskRunner.addError(`Found invalid indexData keys for itemid ${item.itemid}: ${invalidKeys.join(", ")}`);

			const line = JSON.stringify(indexData);
			linesByteUsage+=line.length;
			lines.push(line);

			if(linesByteUsage>MAX_LINES_BYTES_WAIT_THRESHOLD)
				await xu.waitUntil(() => linesByteUsage<MAX_LINES_BYTES_RESUME_THRESHOLD);

			delete fileData.indexData;
			await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));
			taskRunner.increment();
		});
	}

	finishedFindingLines = true;
	await activeLineIndexer;

	indexFile.close();
	await runUtil.run("pigz", [indexFilePath]);

	const report = xu.parseJSON(await fileUtil.readTextFile(reportFilePath));
	report.postProcess.indexedCount = indexedCount;
	await fileUtil.writeTextFile(reportFilePath, JSON.stringify(report));

	taskRunner.phaseComplete();
}
