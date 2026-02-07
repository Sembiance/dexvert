import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";

// Phase 9 - Cleanup our fileData (webData) before it's inserted into a sparkey DB
export default async function phase9({itemWebDirPath, taskRunner})
{
	taskRunner.startProgress(0, "Cleaning up webData files...");
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
			delete fileData.indexData;
			delete fileData.filePath;
			if(fileData?.content)
				delete fileData.content.filePath;
			await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));

			taskRunner.increment();
		});
	}

	taskRunner.phaseComplete();
}
