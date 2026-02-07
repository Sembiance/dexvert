import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";
import {Sparkey} from "Sparkey";
import {C, isFileBlocked} from "../ppUtil.js";

const LARGE_FILE_THRESHOLD = xu.MB*250;

// Phase 10: Take all the web/thumb/file data and stick into sparkey dbs
export default async function phase10({item, itemDirPath, itemWebDirPath, itemThumbDirPath, itemFileDirPath, taskRunner})
{
	// WARNING: Do NOT be tempted to parallelize this function as Sparkey does not support multiple writers at once to the same file
	// I suppose in theory you could parallize web/thumb/file but you are already thrashing the disk enough as it is
	for(const [type, typeDirPath] of [["web", itemWebDirPath], ["thumb", itemThumbDirPath], ["file", itemFileDirPath]])
	{
		const webDB = new Sparkey(path.join(itemDirPath, `${item.itemid.toString()}_${type}`));
		await webDB.truncate();
		const folderPaths = await fileUtil.tree(typeDirPath, {nofile : true, sort : true, relative : true});
		folderPaths.unshift("");
		taskRunner.startProgress(0, `Packing type [${type}] sparkey files...`);

		let allFilePaths = [];
		for(const folderPath of folderPaths)
		{
			const filePaths = (await fileUtil.tree(path.join(typeDirPath, folderPath), {nodir : true, nosymlink : true, sort : true, depth : 1})).sortMulti(v => v.toLowerCase());
			taskRunner.setMax(taskRunner.max+filePaths.length);
			allFilePaths = allFilePaths.concat(filePaths);
		}

		const largeFiles = [];

		for(const filePathBatch of allFilePaths.chunk(50))
		{
			const keys = [];
			const vals = [];
			for(const filePath of filePathBatch)
			{
				const fileInfo = await Deno.lstat(filePath);
				if(!await fileUtil.exists(filePath))
				{
					if(!fileInfo.isSymlink)
						taskRunner.addError(`File not found: ${filePath}`);
					continue;
				}

				// need to reconstruct our 'fileid' by basically stripping out C.UTFCHAR and dropping the extra .json from web paths
				const relPath = path.relative(typeDirPath, filePath);
				const sparkeyKey = type==="web" ? path.join(path.dirname(relPath), path.basename(relPath, ".json")).strip(C.UTFCHAR) || "/" : relPath.strip(C.UTFCHAR);
				if(type==="web" || !isFileBlocked(item, sparkeyKey.strip(C.UTFCHAR)))
				{
					if(fileInfo.size>LARGE_FILE_THRESHOLD)
					{
						largeFiles.push({sparkeyKey, filePath});
					}
					else
					{
						keys.push(sparkeyKey);
						vals.push(await Deno.readFile(filePath));
					}
				}
			}

			if(keys.length>0)
			{
				webDB.putMany(keys, vals);
				taskRunner.incrementBy(keys.length);
			}
		}

		for(const {sparkeyKey, filePath} of largeFiles)
		{
			await webDB.putFile(sparkeyKey, filePath);
			taskRunner.incrementBy(1);
		}

		webDB.unload();
	}

	taskRunner.phaseComplete();
}
