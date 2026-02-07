import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import {C, isFileBlocked} from "../ppUtil.js";
import {path} from "std";
import {AgentPool} from "AgentPool";

// Phase 3 - determine content info & generate thumbs
export default async function phase3({item, itemWebDirPath, itemThumbDirPath, itemFileDirPath, taskRunner, reportFilePath, xlog})
{
	let directoryCount=0;
	const thumbs = [];

	await fileUtil.unlink(C.POLY_TMP_DIR, {recursive : true});
	await Deno.mkdir(C.POLY_TMP_DIR, {recursive : true});

	const folderPaths = await fileUtil.tree(itemWebDirPath, {nofile : true, sort : true, relative : true});
	folderPaths.unshift("");
	taskRunner.startProgress(folderPaths.length, "Finding thumbs and assigning content info...");
	for(const folderPath of folderPaths)
	{
		const folderData = {};

		const jsonPaths = (await fileUtil.tree(path.join(itemWebDirPath, folderPath), {nodir : true, regex : /\.json$/i, sort : true, depth : 1, relative : true})).sortMulti(v => v.toLowerCase());
		taskRunner.setMax(taskRunner.max+jsonPaths.length);

		let nextViewURL = null;
		for(const jsonPath of Array.from(jsonPaths).reverse())
		{
			const webFilePath = path.join(itemWebDirPath, folderPath, jsonPath);
			const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));

			if(nextViewURL)
				fileData.nextViewURL = nextViewURL;
			nextViewURL = path.join("/", "view", item.itemid.toString(), fileData.fileid).encodeURLPath();

			await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));
		}

		await jsonPaths.parallelMap(async jsonPath =>
		{
			const webFilePath = path.join(itemWebDirPath, folderPath, jsonPath);
			const fileData = xu.parseJSON(await fileUtil.readTextFile(webFilePath));
			
			const subParentDirPath = path.join(itemWebDirPath, folderPath, path.dirname(jsonPath), path.basename(jsonPath, C.WEB_SUFFIX));
			const subFilePaths = await fileUtil.tree(subParentDirPath, {nodir : true, regex : /\.json$/i, sort : true, depth : 1});
			const subDirPaths = (await fileUtil.tree(subParentDirPath, {nofile : true, sort : true, depth : 1})).subtractAll(subFilePaths.map(subFilePath => path.join(path.dirname(subFilePath), path.basename(subFilePath, C.WEB_SUFFIX))));
			const subFiles = (await subFilePaths.parallelMap(async kidFilePath => xu.parseJSON(await fileUtil.readTextFile(kidFilePath)))).sortMulti([o => o.filename]);

			if(fileData.dexid.family==="document" && subFiles.length===1 && subFiles[0].pageCount)	// we don't check lineCount here because weare only dealing with 'document' conversion which only shows # Pages in UI
				fileData.pageCount = subFiles[0].pageCount;

			// time to handle content specific properties: url/width/height/duration/animated/etc
			const setContent = function setContentProperties(t)
			{
				fileData.content = {};
				fileData.contentURL = path.join("/", "file", item.itemid.toString(), t.fileid);
				if(fileData.fileid!==t.fileid)
				{
					fileData.content.fileid = t.fileid;
					fileData.content.filePath = t.filePath;
					fileData.content.formatid = t.formatid;
				}
				for(const k of ["width", "height", "duration", "animated"])
				{
					if(t?.dexData?.phase?.meta?.[k])
						fileData[k] = ["animated"].includes(k) ? true : t.dexData.phase.meta[k];
				}
				if(fileData.meta!==t.meta)
					fileData.content.meta = t.meta;
				if(fileData.dexid!==t.dexid)
					fileData.content.dexid = t.dexid;

				if(!Object.keys(fileData.content).length)
					delete fileData.content;
			};

			const setDefaultContent = function setDefaultContentProperties()
			{
				fileData.width = C.DEFAULT_IMG_WIDTH;
				fileData.height = C.DEFAULT_IMG_HEIGHT;
				fileData.contentURL = C.DEFAULT_IMG_URL;
			};

			const browserFormats = Object.values(C.BROWSER_FORMATS).flat();

			// Now we need to determine what 'content' should be used for this file (url/width/height, etc)
			if(browserFormats.includes(fileData.dexid.formatid) && subFiles.length===0)
			{
				// this file is a browser format and has no children, so use this as the content
				// we check children because some browser formats like GIF can be corrupted but I convert to PNG but need to use THAT as the content and not the original GIF
				// example: http://dev.discmaster.textfiles.com/view/3/World's%20Best%20Butts%20(1995).iso/butts00/butts09.gif
				setContent(fileData);
			}
			else if((subFiles.length===1 || (C.IMAGE_VARIANT_FORMATS.includes(fileData.dexid.formatid) && subFiles.length>0)) && !C.ARCHIVE_LIKE.includes(fileData.dexid.family) && browserFormats.includes(subFiles[0].dexid.formatid))
			{
				// this file is not archive like and has either has a single twig kid in a browser format, or this twig is an 'IMAGE VARIANT' type file (like amiga .info) and the first kid is browser friendly, so just use that
				setContent(subFiles.at(C.IMAGE_VARIANT_FORMATS_LAST.includes(fileData.dexid.formatid) ? -1 : 0));
			}
			else if(fileData.dexid.family==="image" && subFiles.length===2)
			{
				// we are an image and have exactly two kid twigs, if 1 is PNG and the other is SVG/WEBP/GIF, then use the PNG file as the content
				const subFileFormats = subFiles.map(o => o.dexid.formatid);
				if(subFileFormats.includes("png") && (subFileFormats.includes("svg") || subFileFormats.includes("webp") || subFileFormats.includes("gif")))
					setContent(subFiles.find(o => o.dexid.formatid==="png"));
				else if(subFileFormats.includes("webp") && subFileFormats.includes("svg"))	// image/aniST
					setContent(subFiles.find(o => o.dexid.formatid==="webp"));
				else
					setDefaultContent();
			}
			else if(fileData.dexid.family==="image")
			{
				// we either have >1 kid or we have exactly 1 kid but it's not a browser format
				setDefaultContent();
			}
			else if(["document", "other"].includes(fileData.dexid.family) && subFiles.length===1 && subFiles[0].dexid.family==="text")
			{
				// some documents convert to txt and 'simple' formats from 'other' category also convert to text
				setContent(subFiles[0]);
			}

			fileData.href = path.join("/", "view", item.itemid.toString(), fileData.fileid);

			let keepViewLink = false;
			if(["document", "other"].includes(fileData.dexid.family) && subFiles.length===1 && (browserFormats.includes(subFiles[0].dexid.formatid) || subFiles[0].dexid.family==="text"))
				keepViewLink = true;

			if((subFiles.length + subDirPaths.length)>1 || ((subFiles.length+subDirPaths.length)===1 && (!fileData.contentURL || fileData.contentURL===C.DEFAULT_IMG_URL) && !keepViewLink))
			{
				fileData.subCount = subFiles.length + subDirPaths.length;
				fileData.href = path.join("/", "browse", item.itemid.toString(), fileData.fileid);
			}

			fileData.href = fileData.href.encodeURLPath();
			fileData.contentURL &&= fileData.contentURL.encodeURLPath();

			fileData.width &&= Math.floor(fileData.width);
			fileData.height &&= Math.floor(fileData.height);

			delete fileData.dexData;

			folderData[fileData.family] ||= [];
			folderData[fileData.family].push(fileData.fileid);

			if(isFileBlocked(item, fileData.fileid))
				fileData.blocked = true;
			
			if([...C.BROWSER_FORMATS.image, ...C.BROWSER_FORMATS.video, ...C.BROWSER_FORMATS.poly].includes(fileData.dexid.formatid))
				thumbs.push({...fileData, itemWebDirPath, itemFileDirPath, itemThumbDirPath, liveOutput : xlog.atLeast("info")});

			await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));
			taskRunner.increment();
		}, Math.floor(navigator.hardwareConcurrency*0.6));

		const folderSubDirPaths = (await fileUtil.tree(path.join(itemWebDirPath, folderPath), {nofile : true, sort : true, depth : 1, relative : true})).subtractAll(jsonPaths.map(v => path.basename(v, C.WEB_SUFFIX)));
		for(const folderSubDirPath of folderSubDirPaths)
		{
			const dirData = {filename : path.basename(folderSubDirPath)};
			dirData.href = path.join("/", "browse", item.itemid.toString(), folderPath.strip(C.UTFCHAR), folderSubDirPath.strip(C.UTFCHAR)).encodeURLPath();
			
			const dirSubParentDirPath = path.join(itemWebDirPath, folderPath, folderSubDirPath);
			const dirSubFilePaths = await fileUtil.tree(dirSubParentDirPath, {nodir : true, regex : /\.json$/i, sort : true, depth : 1, relative : true});
			
			const dirSubDirPaths = await fileUtil.tree(dirSubParentDirPath, {nofile : true, sort : true, depth : 1, relative : true});
			dirData.subCount = dirSubFilePaths.length + dirSubDirPaths.subtractAll(dirSubFilePaths.map(v => path.basename(v, C.WEB_SUFFIX))).length;

			folderData.directory ||= [];
			folderData.directory.push(dirData);
		}

		const webFolderFilePath = path.join(itemWebDirPath, folderPath.strip(C.UTFCHAR), C.WEB_SUFFIX);
		if(path.dirname(webFolderFilePath)!==itemWebDirPath && !await fileUtil.exists(`${path.dirname(webFolderFilePath)}${C.WEB_SUFFIX}`))
		{
			directoryCount++;
			folderData.folderid = path.relative(itemWebDirPath, path.join(itemWebDirPath, folderPath.strip(C.UTFCHAR)));
		}

		for(const familyid of C.FAMILY)
			folderData[familyid] &&= folderData[familyid].sortMulti();

		await fileUtil.writeTextFile(webFolderFilePath, JSON.stringify(folderData));
		taskRunner.increment();
	}

	const report = xu.parseJSON(await fileUtil.readTextFile(reportFilePath), {});
	report.postProcess.familyCounts.directory = directoryCount;
	await fileUtil.writeTextFile(reportFilePath, JSON.stringify(report));

	if(!thumbs.length)
		return taskRunner.phaseComplete();

	taskRunner.startProgress(thumbs.length, " Building thumbs...");
	await fileUtil.writeTextFile(C.POLY_THUMB_COUNT_FILE_PATH, "0");

	const onSuccess = data =>
	{
		if(data.error)
			taskRunner.addError(data.error);
		taskRunner.increment();
	};

	const buildThumbPool = new AgentPool(path.join(import.meta.dirname, "..", "buildThumb.agent.js"), {onSuccess, xlog});
	await buildThumbPool.init();
	await buildThumbPool.start();
	buildThumbPool.process(thumbs);
	await xu.waitUntil(() => buildThumbPool.empty());
	await buildThumbPool.stop();

	taskRunner.startProgress(1, " Cleaning up thumb temp files...");

	await runUtil.run("killall", ["chrome"]);
	await fileUtil.unlink(C.POLY_TMP_DIR, {recursive : true});
	taskRunner.increment();

	taskRunner.phaseComplete();
}
