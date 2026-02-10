import {xu} from "xu";
import {fileUtil, runUtil, hashUtil, encodeUtil} from "xutil";
import {C} from "../ppUtil.js";
import {path, dateParse} from "std";

const TIKA_TIMEOUT = xu.MINUTE*1.5;
const TEXT_IMAGE_FORMATS =
[
	// ANSI text formats, sometimes they convert into HUGE images that can't be OCR'ed well because when resized down the text isn't readable
	"ans", "artworx", "avatar", "iCEDraw", "pcBoard", "tundra", "xb"
];

// Phase 4 - First pass at filling textContent field
export default async function phase4({item, itemWebDirPath, taskRunner, xlog})
{
	const tikaDirPath = path.join(import.meta.dirname, "..", "tika");
	const tikaOptions =
	{
		detached   : true,
		stdoutNull : true,	// the errors and warnings when Tika gets a file it doesn't understand we can safely ignore since we can't do anything about it anwyays
		stderrNull : true,
		cwd        : tikaDirPath,
		env        : {GENTOO_VM : "openjdk-bin-11"}
	};
	const {p : tikaProc} = await runUtil.run(`java`, ["-jar", "tika-server-standard-3.0.0-BETA.jar", "--config", path.join(tikaDirPath, "tika-config.xml"), "--host", "127.0.0.1", "--port", C.TIKA_PORT], tikaOptions);
	await xu.waitUntil(async () => (await (await fetch(`http://127.0.0.1:${C.TIKA_PORT}/`).catch(() => {}))?.text())?.includes("Welcome to the Apache Tika"));

	const itemOriginalFileids = (item.files || []).map(o => o.filePath);

	taskRunner.startProgress(0, "Extracting textContent and updating metadata...");
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
			
			// if we are not a file or folder, just skip it (basically browseable files get a §.json file in their folder, but we don't index that as it's covered by the file itself)
			if(!fileData.fileid && !fileData.folderid)
				return taskRunner.increment();

			const indexData =
			{
				itemid      : item.itemid,
				cat         : item.categoryid,
				genre       : item.genreid,
				textContent : [],
				unsupported : !!fileData.dexid?.unsupported
			};

			if(fileData.folderid)
			{
				// pure folder, not the result of a file
				indexData.fileid = fileData.folderid;
				indexData.name = path.basename(fileData.folderid);
				indexData.family = 0;	// 0 is hardcoded to be: "directory"
				indexData.format = "directory";
				indexData.b3sum = await hashUtil.hashData("blake3", `${item.itemid}${fileData.folderid}`);
			}
			else
			{
				for(const [from, to] of [["fileid", "fileid"], ["filename", "name"], ["ext", "ext"]])
					indexData[to] = fileData[from];

				if(fileData.animated)
					indexData.animated = true;

				indexData.family = C.FAMILY.indexOf(fileData.family);
				indexData.format = fileData.formatid || "unknown";

				for(const k of ["duration", "width", "height", "size"])
				{
					if(fileData[k])
						indexData[k] = Math.floor(+fileData[k]);
				}

				// ts should be ms since 1970
				indexData.ts = dateParse(`${fileData.ts} 12:12:12`, "yyyy-MM-dd HH:mm:ss").getTime();

				// we can truncate this to a smaller value safely, just risks collisions. Blake3 default is 256bits (32 chars). At 128bits (16 chars) it's near zero chance of collision. At 64bits (8 chars) it's a 10% chance of collision with 2 billion files
				indexData.b3sum = fileData.b3sum;

				// get our detections and some other id meta data for our detections field
				let detectionTerms = [];
				if(fileData?.ids?.length)
				{
					detectionTerms = detectionTerms.concat(fileData.ids.map(id => id.formatid || ""));
					detectionTerms = detectionTerms.concat(fileData.ids.map(id => (id.magic || "").split(" ")));
				}

				if(fileData?.idMeta?.macFileType)
					detectionTerms.push(fileData.idMeta.macFileType);
				if(fileData?.idMeta?.macFileCreator)
					detectionTerms.push(fileData.idMeta.macFileCreator);
				if(fileData?.idMeta?.proDOSType)
					detectionTerms.push(`${fileData.idMeta.proDOSType} ${fileData.idMeta.proDOSTypePretty || ""}${fileData.idMeta.proDOSTypeAux?.length ? ` (0x${fileData.idMeta.proDOSTypeAux})` : ""}`);

				if(!["symlink"].includes(indexData.format) && await fileUtil.exists(fileData.filePath) && !(await Deno.stat(fileData.filePath)).isDirectory)	// 34150/file/project-uru-data-collection.iso/mac/movie/13/gallary/§normal.Cxt
				{
					const bytesHeader = await fileUtil.readFileBytes(fileData.filePath, Math.min(16, fileData.size));
					detectionTerms.push(Array.from(bytesHeader, b => (b>=32 && b<=126 ? String.fromCharCode(b) : "•")).join(""), bytesHeader.asHex());
				}

				const detectionsText = detectionTerms.flat(Number.MAX_VALUE).filter(v => v?.length).unique().join(" ");
				if(detectionsText?.length)
					indexData.d = detectionsText;

				// now time to work on getting our 'text' content
				// comments should be considered textContent to be indexed
				if(fileData.comment)
					indexData.textContent.push(fileData.comment);

				// archive files original to the item should include the ITEM name and description as part of the textContent
				if(itemOriginalFileids.includes(fileData.fileid) && fileData.family==="archive" && item.itemid!==7)
				{
					indexData.textContent.push(item.title);
					if(item.description?.length)
						indexData.textContent.push(item.description);
				}

				// index various metadata from files that may be useful for searching
				[
					// music & video
					"title",

					// music
					"author", "type", "tracker", "instruments",
					
					// font
					"family", "fullName", "postscriptName"
				].forEach(key =>
				{
					if(fileData.meta?.[key])
						indexData.textContent.push(...Array.force(fileData.meta[key]));
				});

				// if we are a text file, read the content directly and decode it with our charset hints
				// we used to just send it to TIKA but it was missing too many things such as: http://discmaster.textfiles.com/view/20/FM%20Towns%20Marty%201%20Free%20Software%20Collection.iso/graphics/makolin/makolin.ggg
				if(fileData.content?.dexid?.family==="text" || fileData.family==="text")
				{
					try
					{
						// NOTE: This could be optimized to read only up to C.MAX_INDEX_CONTENT_SIZE but I've only encountered a handful of files that are too big, such as Item #4265: Virtual Reality StarterKit.iso/sop10000/copyfile.swt/DEMOCNTL.SWT/SWTDEMO.BAT
						// But since this phase never takes very long, and Deno.readFile() doesn't support a max size length directly, meh, just try and catch it
						const textFileContent = await encodeUtil.decode(await Deno.readFile(fileData.content?.filePath || fileData.filePath), fileData.content?.meta?.charSet?.declared || fileData.meta?.charSet?.declared || item.encoding);
						if(textFileContent?.trim()?.length)
							indexData.textContent.push(textFileContent?.trim().slice(0, C.MAX_INDEX_CONTENT_SIZE));
					}
					catch(err)
					{
						taskRunner.addError(`Failed to decode text file of ${fileData.size} bytes (${fileData.fileid}) error: ${err.toString()}`);
					}
					
					// once we checked if HTML and then we parsed it and just indexed the textContent sans the HTML tags
					// but there were some old school object/vrml and other tags that people may want to search for directly, it's not just the text content that matters
					// so even though this will cause searches for normal HTML tags like 'table' and 'script' to come back with a TON of HTML results, it's better than missing out
					//if(textFileContent?.length && (fileData.content?.formatid || fileData.formatid)==="html")
					//	textFileContent = (new DOMParser().parseFromString(textFileContent, "text/html"))?.body?.textContent;
				}
				else
				{
					// now prepare to get content from TIKA
					let contentFilePath = null;
					
					if(fileData.content?.dexid?.formatid==="pdf")
						contentFilePath = fileData.content.filePath;
					
					if(!contentFilePath && TEXT_IMAGE_FORMATS.includes(fileData.formatid))
						contentFilePath = fileData.filePath;

					// now get content from TIKA
					if(contentFilePath)
					{
						const {size} = await Deno.stat(contentFilePath);
						if(size<C.MAX_TIKA_SIZE)	// skip files that are too big to be indexed safely
						{
							const {stdout : tikaContent} = await runUtil.run("curl", ["--silent", "--max-time", TIKA_TIMEOUT/xu.SECOND, "-T", contentFilePath, `http://127.0.0.1:${C.TIKA_PORT}/tika`, "--header", "Accept: text/plain"]);
							if(tikaContent.trim().length>0)
								indexData.textContent.push(tikaContent.trim().slice(0, C.MAX_INDEX_CONTENT_SIZE));
						}
					}
					/*else
					{
						// here was an attempt to get strings from the file since we didn't get content from it another way
						// If you ever re-instate this, it needs to filter out any files we've processed (like no sense extracting strings from a ZIP we have extracted or an image we've decoded)
						// also the heuristics can be vastly improved to filter out more garbage than this. Also speed, this was coded in javascript but is likely slow
						const lines = [];
						const stdoutcb = line =>
						{
							line = line.replaceAll(/[\t\n\r]/g, " ").innerTrim().trim();
							if(!line.length)
								return;

							let punct = 0;
							let lastChar = null;
							let repeats = 0;
							for(const c of line.split(""))
							{
								if(c===lastChar)
									repeats++;
								
								// now if c is not a A-Za-z0-9 or whitespace, we consider it a punctuation
								if(!(/[A-Za-z\d\s]/).test(c))
									punct++;

								if(repeats===3 || punct===3)
									return;

								lastChar = c;
							}

							lines.push(line);
						};
						await runUtil.run("strings", ["--all", "--bytes=10", fileData.filePath], {stdoutcb});
						const stringsContent = lines.unique().join(" ");
						if(stringsContent?.length)
							indexData.textContent.push(stringsContent);
					}*/
				}
			}

			indexData.name = indexData.name.replaceAll(/\s/g, " ").innerTrim().trim();

			fileData.indexData = indexData;
			
			await fileUtil.writeTextFile(webFilePath, JSON.stringify(fileData));
			taskRunner.increment();
		});
	}, taskRunner.folderParallelism);

	await runUtil.kill(tikaProc);

	taskRunner.phaseComplete();
}
