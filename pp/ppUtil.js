import {xu} from "xu";
import {path, getAvailablePort} from "std";
import {runUtil, fileUtil} from "xutil";

const C = {};
C.POLY_THUMB_DEFAULT_FPS = 20;
C.POLY_THUMB_DEFAULT_ROTATE_SPEED = 180;
C.CLASSIFY_GPU_COUNT = 1;
C.MAX_TIKA_SIZE = xu.MB*25;	// Don't send files larger than this to tika (note, this isn't a limit on how much gets indexes, just what is 'sent' to tika)
C.MAX_TEXT_INDEX_SIZE = xu.MB*6;
C.MAX_INDEX_CONTENT_SIZE = xu.MB*7;
C.CLASSIFY_IMAGE_DIM_MIN = "50x50";
C.CLASSIFY_IMAGE_DIM_MAX = "1500x1500";

C.UTFCHAR = "§";
C.WEB_SUFFIX = `${C.UTFCHAR}.json`;

C.TIKA_PORT = 17675;

C.POST_PROCESS_HOST = "127.0.0.1";
C.POST_PROCESS_PORT = 17532;

C.POLY_THUMB_HEIGHT = 300;
C.POLY_THUMB_WIDTH = 200;
C.CONVERT_ARGS = ["-define", "filename:literal=true"];
C.CONVERT_PNG_ARGS = [...C.CONVERT_ARGS, "-define", "png:exclude-chunks=time"];
C.DEXVERT_TMP_DIR = "/mnt/dexvert/tmp";
C.POLY_TMP_DIR = path.join(C.DEXVERT_TMP_DIR, "poly");
C.DEFAULT_IMG_URL = "/image/multipleImages.png";
C.DEFAULT_IMG_WIDTH = 128;
C.DEFAULT_IMG_HEIGHT = 128;
C.FAMILY = ["directory", "archive", "image", "audio", "music", "video", "font", "document", "text", "executable", "poly", "other", "unknown"];	// WARNING! DO NOT CHANGE THIS ORDER! Database field family is indexed by this order
C.POLY_THUMB_COUNT_LOCK_FILE_PATH = "/mnt/ram/tmp/buildThumbPoly.lock";
C.POLY_THUMB_COUNT_FILE_PATH = "/mnt/ram/tmp/buildThumbPoly.count";
C.MAX_POLY_THUMB_ACTIVE = 15;

C.BROKEN_IMAGE_FILE_PATH = path.join(import.meta.dirname, "image", "broken.png");

C.BROWSE_THUMB_WIDTH = 175;
C.BROWSE_THUMB_HEIGHT = 150;

C.BROWSE_FONT_THUMB_WIDTH = 350;
C.BROWSE_FONT_THUMB_HEIGHT = 200;

C.BROWSE_VIDEO_THUMB_WIDTH = 320;
C.BROWSE_VIDEO_THUMB_HEIGHT = 200;

C.SEARCH_VISUAL_VECTOR_LENGTH = 768;
C.SEARCH_AUDITORY_VECTOR_LENGTH = 512;

C.NSFW_RACY_MAX = 40;
C.OFFENSIVE_CONFIDENCE =
{
	UNKNOWN       : 0,
	VERY_UNLIKELY : 1,
	UNLIKELY      : 2,
	POSSIBLE      : 3,
	LIKELY        : 4,
	VERY_LIKELY   : 5
};

C.ARCHIVE_LIKE = ["archive", "executable"];
C.BROWSER_FORMATS =
{
	audio    : ["mp3"],
	document : ["pdf", "html"],
	image    : ["gif", "jpg", "png", "svg", "webp"],
	poly     : ["glTF"],
	video    : ["mp4"]
};
// these image formats produce multiple variants of a single image and so we should just grab the first image as the 'thumbnail' on the browse page
C.IMAGE_VARIANT_FORMATS =
[
	"ico",
	"info",
	"multipartJPEG",
	"newIcon",
	"psd",
	"xCursor",

	// sometimes a TIFF file (CD Front (Alt.).tif) will have more than one sub file, just pick the first one as the thumb
	"tiff",

	// often times mac PICT files contain multiple sub files (5_clamsh.ell, bbq), best to just pick one as a representive thumb (see dexvert to-do item to optimize this)
	"pict",

	// usually just contains different bitdepths of the same image, or a hover on/hover off state, just pick the best option
	"palmBitmap"
];

// see above, these should pick the last child image, not the first
C.IMAGE_VARIANT_FORMATS_LAST = ["palmBitmap", "xCursor"];

/* eslint-disable @stylistic/no-multi-spaces, @stylistic/array-bracket-spacing, @stylistic/indent */
/* Arranged in a table to make it easier to read, but will be converted into key : value pairs */
// optional: true means that the field is optional
//    facet: true means that the field is facetable (group by)
//     sort: true means that the field is sortable
//    store: true means that the field's value is stored in the index and is retrievable (rather than just used for searching)
//   ranges: if set to an array of 2 values, represents the min and max range for this key
// WARNING! THIS table is kind of a hold-over from when manticore/typesense was used. BUT despite having a lot of this reproduced in elastic.js, this is still used for several things
// SO THUS, continue to keep this table populated with new columns/fields until such a time that I choose to refeactor it/remove it
C.SEARCH_SCHEMA =
{
	  _options  : [ "type",   "optional", "facet", "sort", "store" ],
	       name : [   "text",  false,      false,   true,   false  ],
	          t : [   "text",  true,       false,   false,  false  ],	// t===text content ('text' is reserved keyword in some dbs and 'content' could be confused with fileData.content.*)
	        ext : [   "text",  true,       false,   false,  false  ],
		      d : [   "text",  true,       false,   false,  false  ],

	     fileid : [ "string",  false,      false,   false,  true   ],	// value stored in this field may be a fileid or folderid
	      b3sum : [ "string",  true,       true,    true,   false  ], 	// optional because directories don't have them. facet is true so GROUP BY can filter out duplicates. sort is true for quasi-random sort

		  addts : [ "uint64",  false,      false,   true,   false  ],	// used to store the time when the item was FIRST indexed (firstInjestedOn from item sql table)
	       size : [ "uint64",  true,       false,   true,   false  ],	// directories don't have a size (they still have a fileid, which is used to look up the §.json folder JSON which has a count)
	         ts : [ "uint64",  true,       false,   true,   false  ],	// Date.now of course is only filled in on server start, but this is good enough as nothing in the DB should be anywhere close to this new

	     itemid : [ "uint32",  false,      true,    true,   true   ],
	   duration : [ "uint32",  true,       false,   true,   false  ],
	      width : [ "uint32",  true,       false,   true,   false  ],
	     height : [ "uint32",  true,       false,   true,   false  ],

	      genre : [ "uint16",  false,      true,    false,  false  ],
	     format : [ "uint16",  true,       true,    false,  false  ],	// if we were not able to identify a file, it has no format

	     family : [  "uint8",  false,      true,    false,  true   ],	// non-optional because we set family to 'unknown' if we don't know and 'directory' for directories
	        cat : [  "uint8",  false,      true,    false,  false  ],
	       nsfw : [  "uint8",  true,       false,   false,  false  ], // h===hash ('hash' is a reserved keyword in some dbs)

	   animated : [   "bool",  true,       false,   false,  false  ],
	unsupported : [   "bool",  true,       false,   false,  false  ],

	          v : [   "fvec",  true,       false,   false,  false  ],	// 768 count float vector for images/poly thumbs, used for similarity search
			 va : [   "fvec",  true,       false,   false,  false  ]	// 512 count float vector for audio, used for similarity search
};
/* eslint-enable @stylistic/no-multi-spaces, @stylistic/array-bracket-spacing, @stylistic/indent */
C.SEARCH_SCHEMA = Object.fromEntries(Object.entries(C.SEARCH_SCHEMA).map(([fieldKey, fieldOptions]) => ([fieldKey, Object.fromEntries(fieldOptions.map((k, i) => ([C.SEARCH_SCHEMA._options[i], k])))])));
delete C.SEARCH_SCHEMA._options;

C.EXTRA_INDEX_KEYS = ["textContent", "ocrText", "transcriptionText", "offensive"];	// these keys are present in the index files but are not to be indexed into the search engine
export {C};

export function isFileBlocked(item, fileid)
{
	return fileid?.length && (item?.blocks || []).some(({block}) => block.startsWith(fileid) || fileid.startsWith(block));
}

export async function classify({taskRunner, xlog, filesToProcess, itemClassifyDirPath, filesDirPath, type, libraries, preProcess, preProcessSuffix, processor, filesAtOnce=10, startTimeout=xu.MINUTE*5, processTimeout=xu.MINUTE*10})
{
	const cwd = path.join(import.meta.dirname, type);
	const env = {
		VIRTUAL_ENV     : path.join(cwd, "env"),
		HOME            : path.join(cwd, "home"),
		LD_LIBRARY_PATH : libraries.map(v => path.join(cwd, "env", "lib", "python3.10", "site-packages", v)).join(":"),
		PATH            : `${path.join(cwd, "env", "bin")}:/usr/local/cuda/bin:${Deno.env.get("PATH")}`
	};
	const python3Path = path.join(cwd, "env/bin/python3");

	let typeDirPath = null;
	if(preProcess)
	{
		typeDirPath = path.join(itemClassifyDirPath, type);
		await Deno.mkdir(typeDirPath, {recursive : true});
		for(const o of filesToProcess)
			o.typeFilePath = path.join(typeDirPath, `${path.basename(o.filePath)}${preProcessSuffix || ""}`);

		if(await fileUtil.exists(path.join(cwd, `${type}PreProcess.js`)))
		{
			const runOptions = runUtil.denoRunOpts({cwd});
			if(xlog.atLeast("info"))
				runOptions.stderrcb = line => xlog.warn`${xu.bracket(`PreProcess.js ${type}`)} ${line}`;
			await runUtil.run("deno", runUtil.denoArgs(`${type}PreProcess.js`, filesDirPath, typeDirPath), runOptions);
		}
		else
		{
			taskRunner.startProgress(filesToProcess.length, `Pre-Processing files [${type}]...`);
			const runOptions = {cwd, stdoutcb : () => taskRunner.increment(), env : {...env, CUDA_VISIBLE_DEVICES : "-1"}};
			if(xlog.atLeast("info"))
				runOptions.stderrcb = line => xlog.warn`${xu.bracket(`PreProcess.py ${type}`)} ${line}`;
			await runUtil.run(python3Path, [`${type}PreProcess.py`, filesDirPath, typeDirPath], runOptions);
		}
	}

	taskRunner.startProgress(filesToProcess.length, `Classifying files [${type}]...`);
	await Deno.mkdir(path.join(cwd, "home"), {recursive : true});
	const startServer = async gpuNum =>
	{
		const r = {gpuNum, port : getAvailablePort()};

		const {p, cb} = await runUtil.run(python3Path, [`${type}Server.py`, "--web_port", r.port.toString()], {detached : true, cwd, env : {...env, CUDA_VISIBLE_DEVICES : gpuNum.toString()}});
		r.p = p;
		r.cb = cb;

		if(!(await xu.waitUntil(async () => (await xu.tryFallbackAsync(async () => await xu.fetch(`http://127.0.0.1:${r.port}/status`, {silent : true})))==="a-ok", {timeout : startTimeout})))
		{
			taskRunner.addError(`${type} server failed to start on port ${r.port} within ${startTimeout.msAsHumanReadable({short : true})}. Will try again, so if no more errors, ok to verify.`);
			await runUtil.kill(p);
			await cb();
			return null;
		}

		return r;
	};

	const servers = await [].pushSequence(0, C.CLASSIFY_GPU_COUNT-1).parallelMap(async gpuNum =>
	{
		let server = null;
		await xu.waitUntil(async () => { server = await startServer(gpuNum); return !!server; });
		return server;
	});

	const serverRestartCounts = {};

	const restartServer = async server =>
	{
		await runUtil.kill(server.p);
		await server.cb();

		serverRestartCounts[server.gpuNum] ||= 0;
		serverRestartCounts[server.gpuNum]++;
		if(serverRestartCounts[server.gpuNum]>3)
		{
			console.error(`${type} server on GPU ${server.gpuNum} has failed to restart ${serverRestartCounts[server.gpuNum]} times, giving up!\nWARNING! batch will be SKIPPED!`);
			return false;
		}

		Object.assign(server, await startServer(server.gpuNum));
		return true;
	};

	const availableServers = Array.from(servers);
	const fileBatches = filesToProcess.chunk(filesAtOnce);

	const processBatch = async (server, fileBatch) =>
	{
		const serverStatus = await xu.fetch(`http://127.0.0.1:${server.port}/status`, {timeout : xu.SECOND*5});
		if(serverStatus!=="a-ok")
		{
			taskRunner.addError(`${type} server failed a status check with status ${serverStatus} (restarting ${type} server, if no more errors appear, ok to accept results)`);
			await restartServer(server);
		}

		const results = await xu.fetch(`http://127.0.0.1:${server.port}/process`, {timeout : processTimeout, asJSON : true, json : {filePaths : fileBatch.map(o => o[preProcess ? "typeFilePath" : "filePath"])}});
		if(results?.length!==fileBatch.length)
		{
			taskRunner.addError(`${type} results length mismatch! ${results?.length} vs ${fileBatch.length}`, true);
			if(!(await restartServer(server)))
				return true;	// if we've restarted the server too many times, it'll return false, in which case we should return true which wil abandon this batch
			return false;
		}

		taskRunner.incrementBy(fileBatch?.length || 0);
		await processor(fileBatch, results);
		availableServers.push(server);
		return true;
	};

	while(fileBatches.length)
	{
		let availableServer = null;
		await xu.waitUntil(() => { availableServer = availableServers.shift(); return !!availableServer; });
		const fileBatch = fileBatches.pop();
		if(!fileBatch?.length)
		{
			availableServers.push(availableServer);
			continue;
		}

		xu.waitUntil(async () => await processBatch(availableServer, fileBatch));
	}

	await xu.waitUntil(() => availableServers.length===servers.length);	// wait for batches to finish

	await servers.parallelMap(async ({p, cb}) =>
	{
		await runUtil.kill(p);
		await cb();
	});

	if(typeDirPath)
		await fileUtil.unlink(typeDirPath, {recursive : true});
}

