import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, runUtil, printUtil, hashUtil, webUtil, urlUtil} from "xutil";
import {path} from "std";
import {DEXRPC_HOST, DEXRPC_PORT, initRegistry} from "../dexUtil.js";
import {OS_SERVER_HOST, OS_SERVER_PORT} from "../osUtil.js";
import {flexMatch} from "../identify.js";
import {DexFile} from "../DexFile.js";
import {formats} from "../format/formats.js";
import {IGNORE_MAGICS, WEAK_MAC_TYPE_CREATORS, WEAK_MAC_TYPES, WEAK_PRODOS_TYPES} from "../WEAK.js";
import {_PRO_DOS_TYPE_CODE} from "../program/archive/cadius.js";
import {C} from "../../pp/ppUtil.js";

const DECRECURSE_HOST = "127.0.0.1";
const DECRECURSE_PORT = 17738;
const DESIRED_SAMPLE_COUNT = 10;
const RECURSE_WORK_DIR_PATH = "/mnt/dexvert/recurse";

// these formats we want some extra samples for
const EXTRA_SAMPLE_COUNT = {
	"image/embeddedJPEG" : 20
};

// these formats should not be higlighted for sample inclusion on the admin item page for various resons
const EXCLUDED_SAMPLE_FORMATS = [
	// too big
	"archive/aaruDiskImage",
	"archive/cdi",
	"archive/cloopImage",
	"archive/goosebumpsCFS",
	"archive/hemeraThumbnailsArchive",
	"archive/hostileWatersMNGArchive",
	"archive/iso",
	"archive/mdf",
	"archive/mdx",
	"archive/mTropolisArchive",
	"archive/nrg",
	"archive/sgiVolumeImage",
	"archive/sgsDAT",
	"archive/starTrekOnlineGameData",
	"archive/thumbsUpDatabase",
	"archive/vmwareDiskImage",
	"video/binkEXE",

	// names have to be generic/specific, so can't have more files in the same samples directory
	"archive/installShieldCAB",
	"archive/sarArchive",
	"font/riscOSFont",
	"other/desktopDB",
	"other/desktopDF",
	"other/riscOSFontMetrics",
	"text/debBuildControl",
	"text/flightSimToolkitAirplaneParameters",
	"text/lingoScript",
	"text/linuxKernelSymbolMap",
	"text/linuxMakeConfig",
	"text/magicTextFile",
	"text/windowsAutorun",
	"text/windowsHostsList",

	// modern formats that are 'generated' from others, so often not original. Also pretty modern so no need for many file samples
	"archive/sevenZip",
	"audio/flac",
	"audio/mp3",
	"document/json",
	"document/pdf",
	"font/otf",
	"font/pcf",
	"image/png",
	"image/svg",
	"image/webp",
	"poly/glTF",
	"text/cue",
	"text/csv",
	"text/css",
	"text/json",
	"text/html",
	"text/toc",
	"text/xml",
	"video/mp4",

	// not interesting, or very application specific or have only come across a tiny repeated few over and over
	"archive/activeMime",
	"archive/corelMOSAIC",
	"archive/impactILB",
	"archive/softdiskLibrary",
	"archive/threeDUltraMiniGolfGameData",
	"archive/warriorKingsGameData",
	"document/bankBookForWindows",
	"document/centralPointHelp",
	"document/codeViewHelp",
	"document/czHelp",
	"document/dageshDocument",
	"document/easyCalc",
	"document/epicITS",
	"document/hotHelpCatalog",
	"document/hyperTextVSUM",
	"document/itsInternational",
	"document/kamasOutline",
	"document/newAgeHelp",
	"document/peterNortonHelp",
	"document/proText",
	"document/qAndADocument",
	"document/stFaxScript",
	"document/usefulNotesNote",
	"document/vgaPaint386Help",
	"document/vipPhonebook",
	"document/wingzHelp",
	"image/dataShowGraphic",
	"image/dataShowSprite",
	"image/megaPaintPattern",
	"music/boneShakerArchitect",
	"music/godOfThunderSong",
	"other/amiDockConfig",
	"other/agSIHelpFile",
	"other/compuserveInformationManagerDB",
	"other/cWorthyErrorLibrarian",
	"other/cWorthyOverlay",
	"other/derCertificate",
	"other/iBrowseCookies",
	"other/ibmPCOverlay",
	"other/maxonMultimediaScript",
	"other/metaEditMethodDefinition",
	"other/novellErrorLibrarian",
	"other/qseqProject",
	"other/quickPascalUnit",
	"text/makeselfSFXCompressedArchive",
	"text/neoBookDocument",
	"text/neoPaintHelp",

	// totally useless
	"other/emptyFile",
	"other/identicalBytes",
	"other/nullBytes",
	"other/nullBytesAlternating",
	"other/symlink",

	// rarely encounter this format and unfortuantly garbage tensor doesn't do a good job at detecting the failed conversions
	"image/electronikaBKPIC",
	"image/zbr",

	// often identified against, and usually produces a fairly good image, but it's rarely actually this format, just a very similar dump of pixel data
	"image/imgScan",

	// uhm?
	"archive/appleSingle"
];

const argv = cmdUtil.cmdInit({
	cmdid   : "dexrecurse",
	version : "1.0.0",
	desc    : "Processes <inputPath> converting or extracting files RECURSIVELY",
	opts    :
	{
		programFlag : {desc : "One or more program:flagName:flagValue values. If set, the given flagName and flagValue will be used for program", hasValue : true, multiple : true},
		ignorePath  : {desc : "A path to ignore when encountered and to skip processing and skip recursing into", hasValue : true, multiple : true},
		suffix      : {desc : "What suffix to use for output directories. This is important to avoid clobbering other output files.", defaultValue : "§"},
		headless    : {desc : "Run headless, no GUI"},
		logLevel	: {desc : "Log level to use", hasValue : true, defaultValue : "info"},
		postProcess : {desc : "Perform post processing on the results"},
		itemMetaURL : {desc : "A URL to fetch itemMeta data from, which is passed to postProcess.js", hasValue : true}
	},
	args :
	[
		{argid : "inputPath", desc : "A single file or directory of files to recurse. IF the inputPath is a file that ends with .tar.gz it will be extracted first", required : true},
		{argid : "outputPath", desc : "Specify a directory to stick it all into the directory. Specify a outputName.tar.gz to stick results into a .tar.gz", required : true}
	]});

const xlog = new XLog(argv.headless ? "error" : argv.logLevel);
if(argv.postProcess && !argv.itemMetaURL)
	Deno.exit(xlog.error`--itemMetaURL is required when --postProcess is set!`);

const dexvertOptions = {};

function parseProgramFlags(flags)
{
	const programFlag = {};
	for(const flagRaw of Array.force(flags))
	{
		const [programid, flagKey, flagValue] = flagRaw.split(":");

		if(!Object.hasOwn(programFlag, programid))
			programFlag[programid] = {};
		programFlag[programid][flagKey] = (flagValue===undefined ? true : flagValue);
	}

	return programFlag;
}

if(argv.programFlag)
	dexvertOptions.programFlag = parseProgramFlags(argv.programFlag);

let workDirPath;
const fullOutputPath = path.resolve(argv.outputPath);
if(fullOutputPath.endsWith(".tar.gz"))
{
	if(!(await Deno.stat(path.dirname(fullOutputPath))).isDirectory)
		Deno.exit(xlog.error`Output path parent directory ${path.dirname(fullOutputPath)} is not a directory!`);

	if(await fileUtil.exists(fullOutputPath))
		Deno.exit(xlog.error`Output path ${fullOutputPath} already exists!`);

	if(await fileUtil.exists(RECURSE_WORK_DIR_PATH))
		await fileUtil.unlink(RECURSE_WORK_DIR_PATH, {recursive : true});
	await Deno.mkdir(RECURSE_WORK_DIR_PATH, {recursive : true});
	workDirPath = await fileUtil.genTempPath(RECURSE_WORK_DIR_PATH);
	await Deno.mkdir(workDirPath, {recursive : true});
}
else
{
	if(!await fileUtil.exists(fullOutputPath))
		Deno.exit(xlog.error`Output directory ${fullOutputPath} does not exist!`);

	if((await fileUtil.tree(fullOutputPath)).length>0)
		Deno.exit(xlog.error`Output directory ${fullOutputPath} is not empty!`);
	
	workDirPath = fullOutputPath;
}

const AGENT_COUNT = +(await xu.fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/agentCount`));

const ALL_MAGICS = new Set();
const EXISTING_SAMPLE_FILES = {};
const newSampleFiles = {};
const newMagics = {};
const improvedMagics = {};
const newMacTypeCreators = {};
const newMacTypeCreatorsFormatids = {};
const newProDOSTypes = {};
const idMetaCheckers = [];

await initRegistry(xlog);

for(const magic of IGNORE_MAGICS)
	ALL_MAGICS.add(magic);

for(const format of Object.values(formats))
{
	for(const m of Array.force(format.magic || []))
		ALL_MAGICS.add(m);

	if(format.idMeta)
		idMetaCheckers.push(format.idMeta);
}

xlog.info`Finding existing sample files...`;
const sampleFilePaths = await fileUtil.tree(path.join(import.meta.dirname, "..", "..", "test", "sample"), {nodir : true, relative : true, depth : 3});
for(const sampleFilePath of sampleFilePaths)
{
	const parts = sampleFilePath.split("/");
	const formatid = `${parts[0]}/${parts[1]}`;
	EXISTING_SAMPLE_FILES[formatid] ||= [];
	EXISTING_SAMPLE_FILES[formatid].push(parts[2]);
}

const isExistingMagic = v =>
{
	for(const m of ALL_MAGICS)
	{
		if(flexMatch(v, m))
			return true;
	}

	return false;
};

xlog.info`Starting recurse...`;

const fileDirPath = path.join(workDirPath, "file");
await Deno.mkdir(fileDirPath);

const metaDirPath = path.join(workDirPath, "meta");
await Deno.mkdir(metaDirPath);

const inputFullPath = path.resolve(argv.inputPath);
if((await Deno.stat(inputFullPath)).isFile)
{
	if(inputFullPath.endsWith(".tar.gz"))	// eslint-disable-line unicorn/prefer-ternary
		await runUtil.run("tar", ["-xf", inputFullPath, "-C", fileDirPath]);
	else
		await runUtil.run("rsync", runUtil.rsyncArgs(inputFullPath, path.join(fileDirPath, path.basename(inputFullPath)), {fast : true}));
}
else
{
	await runUtil.run("rsync", runUtil.rsyncArgs(path.join(inputFullPath, "/"), path.join(fileDirPath, "/"), {fast : true}));
}

let fileProgramFlags = {};
const fileProgramFlagFilePath = path.join(fileDirPath, "dexvert_fileProgramFlags.json");
if(await fileUtil.exists(fileProgramFlagFilePath))
{
	fileProgramFlags = xu.parseJSON(await fileUtil.readTextFile(fileProgramFlagFilePath)) || {};
	await fileUtil.unlink(fileProgramFlagFilePath);
}

let taskFinishedCount = 0;
let taskHandledCount = 0;
const originalFiles = await fileUtil.tree(fileDirPath, {nodir : true, relative : true});
const taskQueue = originalFiles.map(v => ({rel : v}));
const taskActive = new Set();
const startedAt = performance.now();

const routes = new Map();
routes.set("/status", async request =>
{
	const query = urlUtil.urlToQueryObject(request?.url);
	const r = {duration : performance.now()-startedAt, taskQueueCount : taskQueue.length, taskActiveCount : taskActive.size, taskFinishedCount, taskHandledCount};
	const oldestTask = Array.from(taskActive).sortMulti([v => v.startedAt])[0];
	if(oldestTask)
	{
		r.oldestTask = oldestTask;
		r.oldestTask.duration = performance.now()-oldestTask.startedAt;
	}

	if(query?.verbose)
	{
		r.rpcStatus = await xu.fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/status`, {asJSON : true});
		r.osStatus = await xu.fetch(`http://${OS_SERVER_HOST}:${OS_SERVER_PORT}/status`, {asJSON : true});
	}

	const postProcessStatus = await xu.fetch(`http://${C.POST_PROCESS_HOST}:${C.POST_PROCESS_PORT}/status`, {asJSON : true, timeout : xu.SECOND, silent : true});
	if(postProcessStatus)
		r.postProcessStatus = postProcessStatus;

	return Response.json(r);
});

const webServer = webUtil.serve({hostname : DECRECURSE_HOST, port : DECRECURSE_PORT}, await webUtil.route(routes), {xlog});
const bar = argv.headless ? null : printUtil.progress({barWidth : 25, max : taskQueue.length});

const SAMPLE_PATH_SUMS = {};
async function isNewSampleFile(dexformatid, sampleFilePath)
{
	if((EXISTING_SAMPLE_FILES[dexformatid]?.length || 0)>=(EXTRA_SAMPLE_COUNT[dexformatid] || DESIRED_SAMPLE_COUNT))
		return false;

	if(EXCLUDED_SAMPLE_FORMATS.includes(dexformatid) || dexformatid.endsWith("GameArchive") || dexformatid.endsWith("GameDataArchive"))
		return false;

	SAMPLE_PATH_SUMS[dexformatid] ||= await (EXISTING_SAMPLE_FILES[dexformatid] || []).parallelMap(async filename => await hashUtil.hashFile("blake3", path.join(import.meta.dirname, "..", "..", "test", "sample", dexformatid, filename)));

	const b3sum = await hashUtil.hashFile("blake3", sampleFilePath);
	if(SAMPLE_PATH_SUMS[dexformatid].includes(b3sum))
		return false;

	return true;
}

async function processNextQueue()
{
	const taskProps = taskQueue.shift();
	if((argv.ignorePath || []).some(ignoredPath => taskProps.rel.strip(argv.suffix).startsWith(ignoredPath)) || path.basename(taskProps.rel, path.extname(taskProps.rel)).endsWith(argv.suffix))
	{
		taskFinishedCount++;
		bar?.increment();
		return;
	}
	
	const task = {relFilePath : taskProps.rel, startedAt : performance.now()};
	taskActive.add(task);

	//const taskLogPrefix = `\n${xu.bracket(`${xu.colon("TASK")}${task.relFilePath}`)}`;
	//xlog.debug`${taskLogPrefix} dexverting...`;

	try
	{
		task.relDirPath = path.dirname(task.relFilePath)==="." ? "" : path.dirname(task.relFilePath);
		task.fileOutDirPath = path.join(fileDirPath, task.relDirPath, `${path.basename(task.relFilePath)}${argv.suffix}`);
		await Deno.mkdir(task.fileOutDirPath, {recursive : true});

		task.metaFilePath = path.join(metaDirPath, task.relDirPath, `${path.basename(task.relFilePath)}.json`);
		task.logFilePath = path.join(metaDirPath, task.relDirPath, `${path.basename(task.relFilePath)}.txt`);
		await Deno.mkdir(path.dirname(task.metaFilePath), {recursive : true});

		const inputFilePath = path.join(fileDirPath, task.relFilePath);
		const rpcData = {op : "dexvert", inputFilePath, outputDirPath : task.fileOutDirPath, logLevel : "debug", dexvertOptions : xu.clone(dexvertOptions)};
		if(taskProps.fileMeta)
			rpcData.fileMeta = taskProps.fileMeta;
		if(taskProps.forbidProgram)
			rpcData.dexvertOptions.forbidProgram = taskProps.forbidProgram;
		if(fileProgramFlags[task.relFilePath])
		{
			rpcData.dexvertOptions.programFlag ||= {};
			Object.assign(rpcData.dexvertOptions.programFlag, parseProgramFlags(fileProgramFlags[task.relFilePath]));
		}

		let {r, log} = xu.parseJSON(await xu.fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {json : rpcData, timeout : (xu.HOUR*2)+(xu.MINUTE*15)}), {}) || {};
		if(!r?.json)
		{
			r = {
				json :
				{
					original  : { input : (await DexFile.create(inputFilePath)).serialize() },
					ids       : [],
					past      : [],
					processed : false,
					duration  : 1
				},
				pretty : `Invalid JSON response from dexrpc for ${task.relFilePath}:\n\tlog: ${JSON.stringify(log)}\n\tr: ${JSON.stringify(r)}`
			};
			log = [r.pretty];
			xlog.error`${r.pretty}`;
		}

		const dexData = r.json;

		const meta = {dexData, dexDuration : performance.now()-task.startedAt, task, originalFile : originalFiles.includes(task.relFilePath)};
		await fileUtil.writeTextFile(task.metaFilePath, JSON.stringify(meta));
		await fileUtil.writeTextFile(task.logFilePath, `${r.pretty}\n${(log || []).join("\n")}`);

		const dexid = (dexData.processed && dexData.phase?.id) ? dexData.phase.id : ((dexData.ids || []).find(({from, unsupported, matchType}) => from==="dexvert" && unsupported && ["magic", "filename"].includes(matchType)) || null);
		if(dexid)
			taskHandledCount++;

		const dexformatid = dexid ? `${dexid.family}/${dexid.formatid}` : null;

		//xlog.debug`${taskLogPrefix} Gathering data for report...`;
		if(dexid && !dexid.unsupported && await isNewSampleFile(dexformatid, inputFilePath))
		{
			newSampleFiles[dexformatid] ||= [];
			newSampleFiles[dexformatid].push(task.relFilePath);
		}
		
		if(dexData.ids?.length)
		{
			for(const id of dexData.ids || [])
			{
				// Skip weak identifications, those from dexvert or magics that match an existing format
				if(id.weak || id.from==="dexvert" || isExistingMagic(id.magic))
					continue;

				const magicsBucket = dexid ? improvedMagics : newMagics;
				magicsBucket[id.magic] ||= [];
				magicsBucket[id.magic].pushUnique(task.relFilePath);
			}
		}

		const macFileType = dexData.idMeta?.macFileType;
		const macFileCreator = dexData.idMeta?.macFileCreator;
		if((macFileType || macFileCreator) && !idMetaCheckers.some(idMetaChecker => idMetaChecker({macFileType, macFileCreator})))
		{
			const macFileTypeCreator = `${macFileType || "????"}/${macFileCreator || "????"}`;
			if(macFileTypeCreator.trim(macFileTypeCreator).length>1 && !WEAK_MAC_TYPE_CREATORS.includes(macFileTypeCreator) && !WEAK_MAC_TYPES.includes(macFileType || "????"))
			{
				newMacTypeCreators[macFileTypeCreator] ||= [];
				newMacTypeCreators[macFileTypeCreator].pushUnique(task.relFilePath);

				if(dexid && !dexid.unsupported)
				{
					newMacTypeCreatorsFormatids[macFileTypeCreator] ||= {};
					newMacTypeCreatorsFormatids[macFileTypeCreator][dexformatid] ||= 0;
					newMacTypeCreatorsFormatids[macFileTypeCreator][dexformatid]++;
				}
			}
		}

		const proDOSType = dexData.idMeta?.proDOSType;
		const proDOSTypeCode = _PRO_DOS_TYPE_CODE[proDOSType];
		if(proDOSType && !idMetaCheckers.some(idMetaChecker => idMetaChecker({proDOSType, proDOSTypeCode, proDOSTypePretty : dexData.idMeta?.proDOSTypePretty, proDOSTypeAux : dexData.idMeta?.proDOSTypeAux})) &&
			(!proDOSTypeCode?.length || !WEAK_PRODOS_TYPES.includes(proDOSTypeCode)))
		{
			const proDOSTypeFull = `${proDOSTypeCode || ""} [${proDOSType}] ${dexData.idMeta?.proDOSTypePretty || ""}${dexData.idMeta?.proDOSTypeAux ? ` (0x${dexData.idMeta?.proDOSTypeAux})` : ""}`.trim();
			newProDOSTypes[proDOSTypeFull] ||= [];
			newProDOSTypes[proDOSTypeFull].pushUnique(task.relFilePath);
		}

		if(!dexData?.created?.files?.output?.length)
		{
			await fileUtil.unlink(task.fileOutDirPath);
		}
		else
		{
			const lastRan = dexData.phase?.ran?.at(-1);	// Could potentially change this to include ALL ran programs with forbidChildRun instead of just the last...
			const forbidProgram = (lastRan?.forbidChildRun && lastRan.programid===dexData.phase.converter) ? [lastRan.programid] : null;

			//xlog.debug`${taskLogPrefix} Adding ${dexData.created.files.output.length.toLocaleString()} output files to task queue...`;
			for(const fileRel of dexData.created.files.output)
			{
				bar?.incrementMax();
				const fileTaskProps = {rel : path.relative(fileDirPath, path.join(dexData.created.root, fileRel))};
				if(forbidProgram)
					fileTaskProps.forbidProgram = forbidProgram;
				if(dexData.phase?.meta?.fileMeta?.[fileRel])
					fileTaskProps.fileMeta = dexData.phase.meta.fileMeta[fileRel];
				taskQueue.push(fileTaskProps);
			}
		}
	}
	catch(err)
	{
		try
		{
			await fileUtil.writeTextFile(task.logFilePath, err.toString(), {append : true});
			if(!await fileUtil.exists(task.metaFilePath))
				await fileUtil.writeTextFile(task.metaFilePath, JSON.stringify({failed : true, err : err.toString(), stack : err.stack}));
		}
		catch(err2)	// eslint-disable-line unicorn/catch-error-name
		{
			xlog.error`Dexrecurse failed to handle file: ${task.relFilePath}`;
			xlog.error`Got exception: ${err}`;
			xlog.error`Failed to write error to log due to error: ${err2}`;
		}
	}

	taskFinishedCount++;
	bar?.increment();
	taskActive.delete(task);
}

await xu.waitUntil(async () =>	// eslint-disable-line require-await
{
	if(taskActive.size===0 && taskQueue.length===0)
		return true;

	while(taskQueue.length>0 && taskActive.size<AGENT_COUNT)
		processNextQueue();	// eslint-disable-line no-floating-promise/no-floating-promise

	const slowestTask = Array.from(taskActive).sortMulti([v => v.startedAt])[0];
	const queuePart = `${xu.cf.fg.chartreuse("Q")} ${xu.cf.fg.white(taskQueue.length.toString())}`;
	const activePart = `${xu.cf.fg.chartreuse("A")} ${xu.cf.fg.white(taskActive.size.toString())}`;
	const handledPart = `${xu.cf.fg.chartreuse("H")} ${((taskHandledCount/taskFinishedCount)*100).toFixed(2)}%`;
	const slowestPart = `${xu.cf.fg.white((performance.now()-slowestTask.startedAt).msAsHumanReadable({short : true}))} ${slowestTask.relFilePath.innerTruncate(40)}`;
	bar?.setStatus(` ${queuePart}   ${activePart}   ${handledPart}   ${slowestPart}`);

	return false;
}, {interval : 100});

const totalDuration = performance.now()-startedAt;
xlog.info`\ndex Duration: ${totalDuration.msAsHumanReadable()}`;

xlog.debug`Preparing reportData...`;
const reportData = {host : Deno.hostname(), duration : totalDuration, finished : taskFinishedCount, handled : taskHandledCount, newSampleFiles, newMagics, improvedMagics, newMacTypeCreators, newMacTypeCreatorsFormatids, newProDOSTypes};

xlog.debug`Writing reportData to: ${path.join(workDirPath, "report.json")}`;
await fileUtil.writeTextFile(path.join(workDirPath, "report.json"), JSON.stringify(reportData));

if(argv.postProcess && argv.itemMetaURL)
{
	xlog.info`Starting post processing...`;
	await runUtil.run("deno", runUtil.denoArgs(path.join(import.meta.dirname, "..", "..", "pp", "postProcess.js"), "--itemMetaURL", argv.itemMetaURL, workDirPath), runUtil.denoRunOpts({liveOutput : true}));
}

await webServer.stop();

if(fullOutputPath.endsWith(".tar.gz"))
{
	await runUtil.run("tar", ["-cf", fullOutputPath.substring(0, fullOutputPath.length-3), "-C", workDirPath, "."]);
	await runUtil.run("pigz", [fullOutputPath.substring(0, fullOutputPath.length-3)]);
	await fileUtil.unlink(workDirPath, {recursive : true});
}
