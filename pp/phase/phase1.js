import {xu} from "xu";
import {fileUtil} from "xutil";
import {C} from "../ppUtil.js";
import {path} from "std";

// Phase 1 - file & directory renaming
export default async function phase1({itemFileDirPath, taskRunner})
{
	const folderPaths = await fileUtil.tree(itemFileDirPath, {nofile : true, sort : true, relative : true});
	folderPaths.unshift("");
	taskRunner.startProgress(folderPaths.length);
	taskRunner.folderCount = 0;
	taskRunner.fileCount = 0;
	for(const folderPath of folderPaths)
	{
		taskRunner.folderCount++;

		const filePaths = await fileUtil.tree(path.join(itemFileDirPath, folderPath), {nodir : true, sort : true, depth : 1, relative : true});
		taskRunner.setMax(taskRunner.max+filePaths.length);
		for(const filePath of filePaths)
		{
			taskRunner.fileCount++;

			try
			{
				await Deno.rename(path.join(itemFileDirPath, folderPath, filePath), path.join(itemFileDirPath, folderPath, `${C.UTFCHAR}${filePath}`));
			}
			catch(err)
			{
				taskRunner.addError(`Failed to handle file ${path.join(itemFileDirPath, folderPath, filePath)} with error:\n${err.stack}\nDELETING FILE FROM DISK (to prevent errors in further phases)`);
				await fileUtil.unlink(path.join(itemFileDirPath, folderPath, filePath));
			}
			taskRunner.increment();
		}
	}

	taskRunner.avgFileCount = taskRunner.fileCount/taskRunner.folderCount;
	taskRunner.folderParallelism = Math.floor(navigator.hardwareConcurrency/taskRunner.avgFileCount);

	for(const folderPath of folderPaths.reverse())
	{
		await Deno.rename(path.join(itemFileDirPath, folderPath), path.join(itemFileDirPath, path.dirname(folderPath), path.basename(folderPath).strip(C.UTFCHAR)));
		taskRunner.increment();
	}

	taskRunner.phaseComplete();
}
