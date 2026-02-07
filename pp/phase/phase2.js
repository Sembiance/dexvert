import {xu} from "xu";
import {fileUtil, hashUtil} from "xutil";
import {C} from "../ppUtil.js";
import {path, dateFormat} from "std";

function getDexid(dexData)
{
	const unknownID = {family : "unknown", formatid : "unknown", magic : "Unknown", unsupported : true};

	if(!dexData)
		return unknownID;

	if(dexData.processed && dexData.phase?.id)
		return dexData.phase.id;
	
	const strongMatchTypes = ["magic", "idMeta", "custom", "filename"];
	return (dexData.ids || []).filter(({from, unsupported, matchType}) => from==="dexvert" && unsupported && strongMatchTypes.includes(matchType)).sortMulti([({matchType}) => strongMatchTypes.indexOf(matchType)])?.[0] || unknownID;
	//return (dexData.ids || []).find(({from, unsupported, matchType}) => from==="dexvert" && unsupported && ["magic", "filename"].includes(matchType)) || unknownID;
}

// Phase 2 - Set some basic things that don't rely on knowing anything about children
export default async function phase2({item, itemFileDirPath, itemMetaDirPath, itemWebDirPath, taskRunner, reportFilePath, xlog})
{
	const stats = { totalBytes : 0, handledCount : 0, fileCount : 0, familyCounts : {}};

	const folderPaths = await fileUtil.tree(itemMetaDirPath, {nofile : true, sort : true, relative : true});
	folderPaths.unshift("");
	taskRunner.startProgress(folderPaths.length, "Setting basic properties...");
	for(const folderPath of folderPaths)
	{
		const jsonPaths = (await fileUtil.tree(path.join(itemMetaDirPath, folderPath), {nodir : true, regex : /\.json$/i, sort : true, depth : 1, relative : true})).sortMulti(v => v.toLowerCase());
		taskRunner.setMax(taskRunner.max+jsonPaths.length);

		let prevViewURL = null;
		for(const jsonPath of jsonPaths)
		{
			const webFilePath = path.join(itemWebDirPath, folderPath.strip(C.UTFCHAR), path.dirname(jsonPath.strip(C.UTFCHAR)), `${path.basename(jsonPath.strip(C.UTFCHAR), ".json")}${C.WEB_SUFFIX}`);
			await Deno.mkdir(path.dirname(webFilePath), {recursive : true});

			const metaData = xu.parseJSON(await fileUtil.readTextFile(path.join(itemMetaDirPath, folderPath, jsonPath)));
			if(metaData.failed)
			{
				taskRunner.addError(`Phase 2: Meta file failed set to true ${itemMetaDirPath} ${folderPath} ${jsonPath}\nHas error [${metaData.err}] with stack:\n${metaData.stack}`);
				continue;
			}

			const dexData = metaData?.dexData;
			if(!dexData)
			{
				taskRunner.addError(`Phase 2: Failed to find dex data in ${itemMetaDirPath} ${folderPath} ${jsonPath}\nReceived: ${JSON.stringify(metaData)}`);
				continue;
			}

			stats.totalBytes += dexData.original.input.size;
			stats.fileCount++;

			const fileData = {};
			fileData.itemid = item.itemid;
			fileData.fileid = path.relative(itemWebDirPath, path.join(itemWebDirPath, folderPath.strip(C.UTFCHAR), path.dirname(jsonPath.strip(C.UTFCHAR)), path.basename(jsonPath.strip(C.UTFCHAR), ".json")));

			for(const key of ["base", "size", "ts", "ext"])
			{
				if(Object.hasOwn(dexData?.original?.input, key) && (typeof dexData.original.input[key]!=="string" || dexData.original.input[key].length>0))
					fileData[key==="base" ? "filename" : key] = key==="ts" ? (dateFormat(new Date(dexData.original.input[key]), "yyyy-MM-dd")) : dexData.original.input[key];
			}

			fileData.comments = [];
			if(dexData?.original?.input?.meta?.comment?.length)
				fileData.comments.push(dexData.original.input.meta.comment);

			// any dates earlier than 1970 are probably invalid
			if(fileData.ts && (+fileData.ts.split("-")[0])<1970)
				delete fileData.ts;

			// if we are original to this item or don't have a timestamp, we should set the ts to the date of our item
			if(metaData.originalFile || !fileData.ts)
				fileData.ts = `${item.year}-01-01`;
		
			const dexid = getDexid(dexData);

			stats.familyCounts[dexid.family] ||= 0;
			stats.familyCounts[dexid.family]++;
			if((dexData.processed && dexData.phase?.id) ? dexData.phase.id : ((dexData.ids || []).find(({from, unsupported, matchType}) => from==="dexvert" && unsupported && ["magic", "custom", "filename"].includes(matchType)) || null))
				stats.handledCount++;

			if(prevViewURL)
				fileData.prevViewURL = prevViewURL;
			prevViewURL = path.join("/", "view", fileData.itemid.toString(), fileData.fileid).encodeURLPath();

			fileData.dexid = dexid;
			fileData.family = dexid.family;
			fileData.formatid = dexid.formatid;
			fileData.formatName = dexid.magic;
			fileData.filePath = path.join(itemFileDirPath, folderPath.strip(C.UTFCHAR), path.dirname(jsonPath).strip(C.UTFCHAR), `${C.UTFCHAR}${path.basename(jsonPath, ".json")}`);
			fileData.b3sum = dexid.formatid==="symlink" || dexData?.original?.input?.isSymlink ? await hashUtil.hashData("blake3", `${fileData.itemid}${fileData.fileid}`) : await hashUtil.hashFile("blake3", fileData.filePath);
			if(dexData.phase?.meta)
				fileData.meta = dexData.phase.meta;

			if(dexid.family==="text" && fileData.meta?.lineCount)
				fileData.lineCount = dexData.phase.meta.lineCount;
			if(dexid.formatid==="pdf" && fileData.meta?.pages)
				fileData.pageCount = dexData.phase.meta.pages;

			if(fileData.meta?.comment)
				fileData.comments.push(dexData.phase.meta.comment);

			fileData.comment = fileData.comments.join("\n");
			delete fileData.comments;
			if(fileData.comment.trim().length===0)
				delete fileData.comment;

			if(dexData?.ids?.length)
				fileData.ids = dexData.ids;
			if(Object.keys(dexData?.idMeta || {})?.length)
				fileData.idMeta = dexData.idMeta;

			if(fileData.meta?.title && !["<no songtitle>", "<unnamed>"].includes(dexData.phase.meta.title.toLowerCase()))
				fileData.title = dexData.phase.meta.title;

			fileData.dexData = dexData;	// This will be deleted in later passes

			try
			{
				await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));
			}
			catch(err)
			{
				taskRunner.addError(`Unable to write file ${webFilePath} to disk for JSON file ${path.join(itemMetaDirPath, folderPath, jsonPath)} with error:\n${err.stack}\nDELETING JSON FILE FROM DISK (to prevent errors in further phases)`);
				await fileUtil.unlink(path.join(itemMetaDirPath, folderPath, jsonPath));
			}
			taskRunner.increment();
		}

		taskRunner.increment();
	}

	const report = xu.parseJSON(await fileUtil.readTextFile(reportFilePath));
	Object.assign(report.postProcess, stats);
	await fileUtil.writeTextFile(reportFilePath, JSON.stringify(report));

	taskRunner.phaseComplete();
}
