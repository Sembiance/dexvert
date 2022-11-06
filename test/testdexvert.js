/* eslint-disable camelcase, prefer-named-capture-group, unicorn/better-regex, sonarjs/no-empty-collection */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, printUtil, runUtil, hashUtil, diffUtil} from "xutil";
import {path, dateFormat, dateParse} from "std";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexvert conversions for 1 or all formats",
	opts    :
	{
		format     : {desc : "Only test a single format: archive/zip", hasValue : true},
		file       : {desc : "Only test sample files that end with this value, case insensitive.", hasValue : true},
		record     : {desc : "Take the results of the conversions and save them as future expected results"},
		report     : {desc : "Output an HTML report of the results."},
		liveErrors : {desc : "Report errors live as they are detected instead of waiting until the end."},
		debug      : {desc : "Used temporarily when attempting to debug stuff"}
	}});

// ensure if we have a format, it doesn't end with a forward slash, we count those to know how far to search deep in samples tree
argv.format = argv.format?.endsWith("/") ? argv.format.slice(0, -1) : argv.format;

// These are relative dir paths from test/sample/ that are just supporting files that need to be here but should be ignored for testing purposes
const SUPPORTING_DIR_PATHS =
[
	"music/Instruments"
];

// these formats have files that won't identify due to not being in the proper disk locations, so we force the format
const FORCE_FORMAT_AS =
[
	"font/amigaBitmapFontContent"
];

const FORMAT_OS_HINT =
{
	"image/printfox" : "commodore",
	"archive/iso"    : {"OS_user_4.0.iso" : "nextstep"},
	"archive/sit"    : {"SAM_4.5.1_Patcher_PPC Fol9633.sit" : "macintoshjp", "StuffIt Expander 6.0J ｲﾝｽﾄｰﾗ" : "macintoshjp"}
};

// these formats produce a single file, but the name is always different
const SINGLE_FILE_DYNAMIC_NAMES =
[
];

const FLEX_SIZE_PROGRAMS =
{
	// the ILBM color shifting program generates different frames each time
	ilbm2frames : 10,

	// Produces slightly different output on archive/powerPlayerMusicCruncher/TESLA GIRLS file, but I imagine it's a general issue with the program
	xfdDecrunch : 0.1,
	
	// Produces different data each time
	amigaBitmapFontContentToOTF : 0.1,
	darktable_cli               : 0.1,
	doomMUS2mp3                 : 0.1,
	Email_Outlook_Message       : 0.1,
	fontforge                   : 0.1,
	fontographer                : 0.1,
	gimp                        : 0.5,
	sidplay2                    : 0.1,
	sndh2raw                    : 0.1,
	soundFont2tomp3             : 0.1,
	zxtune123                   : 0.1
};

const FLEX_SIZE_FORMATS =
{
	archive :
	{
		// different each time due to way it generates frames
		swf    : 5,
		swfEXE : 5,

		// the PBMs generated are different each time
		hypercard : 0.1,

		// different PDF each time
		tnef : 0.1
	},
	document :
	{
		// these conversions sometimes differ WILDLY, haven't figured out why
		hlp        : 50,
		wildcatWCX : 90,
		wordDoc    : 80,

		// PDF generation has lots of embedded things that change from timestamps to unique generate id numbers and other meta data
		"*:.pdf" : 2,

		// HTML generation can change easily too
		"*:.html" : 1
	},
	image :
	{
		// Each iteration generates different clippath ids, sigh.
		dxf : 1,

		// each running produces slightly different output, not sure why, haven't investigated further
		ani              : 15,
		lottie           : 0.1,
		pes              : 0.1,
		rekoCardset      : 0.1,
		ssiTLB           : 0.1,
		windowsClipboard : 0.1,

		// takes a screenshot or a framegrab which can differ slightly on each run
		fractalImageFormat : 7,
		naplps             : 20,
		theDrawCOM         : 5,
		threeDCK           : 10
	},
	video :
	{
		// these are screen recordings from DOSBox and can differ a good bit between each run
		disneyCFAST : 25,
		fantavision : 25,
		grasp       : 40
	}
};

// if any of the OUTPUT FILES from a conversion equal these regexes, then ignore their size completely
const IGNORE_SIZE_FILEPATHS =
[
	/scripts\/.+\.as$/i,			// archive/swf/cookie-hamster often produces very different script/**/*.as files
	/\^\^ sweet heart.png$/,
	/lem2.webp$/,
	/SUB2.webp$/
];

// these files have a somewhat dynamic nature or are CPU sensitive and sometimes 1 or more files are produced or not produced or differ, which isn't ideal, but not the end of the world
// Specific the path to the file and a number of different files that is allowed
const FLEX_DIFF_FILES =
[
	// this specific file sometimes extracts a pict, sometimes a bmp, no idea why
	/archive\/rsrc\/Speedometer 4\.02\.rsrc$/,
	
	// not sure why, but sometimes I get a .txt sometimes I get a .pdf very weird
	/document\/wordDoc\/POWWOW\.DOC$/,
	
	// sometimes various .as scripts are exatracted, sometimes not
	/archive\/swf\/.+$/,
	/archive\/swfEXE\/.+$/
];

// Regex is matched against the sample file tested and the second item is the family and third is the format to allow to match to or true to allow any family/format
const DISK_FAMILY_FORMAT_MAP =
[
	// Mis-classified by tensor as garbage, but they do look like garbage, so we allow it and they get processed as something else instead
	[/image\/bmp\/WATER5\.BMP$/, "archive", true],
	[/image\/vzi\/X\.BIN$/, "image", "binaryText"],
	[/image\/vzi\/Y\.BIN$/, "image", "binaryText"],

	// These are actually mis-identified files, but I haven't come up with a good way to avoid it
	[/archive\/rawPartition\/example\.img$/, "archive", "iso"],
	[/image\/artStudio\/.*\.shp$/, "image", "loadstarSHP"],
	[/image\/binaryText\/goo-metroid\.bin$/, "image", "tga"],
	[/image\/hiEddi\/05$/, "image", "doodleC64"],
	[/image\/doodleAtari\/.*\.art$/i, "image", "asciiArtEditor"],
	[/other\/iBrowseCookies\/.+/, "text", true],
	[/text\/txt\/SPLIFT\.PAS$/, "text", "pas"],

	// These are actually a fallback packed archive, but the other converters are so flexible at handling things they get picked up first, which is ok
	[/archive\/macBinary\/bdh66306\.gif$/, "image", "gif"],

	// These files have garbage on the end that prevent them from detected as what they should be. I used to 'trim' files on a 2nd and 3rd attempt to detect, but now with perlTextCheck, this can't be done and isn't needed
	[/text\/c\/.+\.C/i, "text", "txt"],
	[/text\/latexAUXFile\/LCAU\.AUX$/i, "text", "txt"],

	// These files don't convert with my converters and get identified to other things
	[/image\/cgm\/input\.cgm$/i, "text", "txt"],

	// These formats share generic .ext only, no magic matches
	[/image\/asciiArtEditor\/.+$/, "image", "gfaArtist"],
	[/image\/artistByEaton\/BLINKY\.ART$/, "image", "asciiArtEditor"],
	[/image\/gfaArtist\/.+$/, "image", "asciiArtEditor"],
	[/image\/magicDraw\/.+$/, "image", "a2gsSHStar"],
	[/image\/petsciiSeq\/.+$/, "image", "stadPAC"],
	[/image\/pixelPerfect\/.+$/, "image", true],
	[/image\/pfsFirstPublisher\/.+$/, "image", "artDirector"],

	// Unsupported files that end up getting matched to other stuff
	[/audio\/dataShowSound\/.+/i, "text", true],
	[/document\/hancomWord\/.+/i, "archive", true],
	[/document\/hotHelpText\/.+\.txt$/i, "text", true],
	[/document\/imf\/.+/i, "text", true],
	[/document\/manPage\/glib\.man/i, "text", true],
	[/document\/microsoftPublisher\/.+/i, "archive", true],
	[/document\/pagePlus\/.+/i, "archive", true],
	[/document\/vCard\/.+/i, "text", true],
	[/image\/a2Sprites\/.+/i, "text", true],
	[/image\/excelChart\/.+/i, "document", "xls"],
	[/image\/jpegXL\/JXL\.jxl$/i, "text", true],
	[/image\/neoPaintPattern\/.+/i, "text", true],
	[/music\/renoise\/.+/i, "archive", "zip"],
	[/music\/tss\/.+/i, "text", true],
	[/other\/installShieldHDR\/.+\.hdr/i, "image", "radiance"],
	[/other\/microsoftChatCharacter\/armando.avb$/, "image", "tga"],
	[/poly\/povRay\/.+/i, "text", true],
	[/poly\/vrml\/.+/i, "text", true],
	[/poly\/ydl\/.+/i, "text", true],
	[/unsupported\/emacsCompiledLisp\/FILES\.ELC/i, "text", true],

	// Supporting/AUX files
	[/archive\/(cdi|iso)\/.+\.(cue|toc)$/i, "text", true],
	[/archive\/irixIDBArchive\/license_eoe\.?(books|man|sw|$)/i, true, true],
	[/archive\/pog\/.+\.pnm$/i, "other", true],
	[/image\/fig\/.+\.(gif|jpg|xbm|xpm)$/i, "image", true],
	[/image\/printMasterShape\/.+\.sdr$/i, "other", true],
	[/music\/pokeyNoise\/.+\.info$/i, "image", "info"],
	[/music\/tfmx\/smpl\..+$/i, true, true],
	[/other\/installShieldHDR\/.+\.(cab|hdr)/i, "archive", true],
	[/other\/pogNames\/.+\.pog$/i, "archive", true],
	[/other\/printMasterShapeNames\/.+\.shp$/i, "image", true]
];

// Normally if a file is unprocessed, I at least require an id to the disk family/format, but some files can't even be matched to a format due to the generality of the format
const UNPROCESSED_ALLOW_NO_IDS =
[
	"archive/rar",
	"image/bbcDisplayRAM",
	"image/teletext",
	"music/richardJoseph",
	"other/iBrowseCookies",		// Must match filename 'Cookies' but can't have more than 1 with that extension
	"unsupported/binPatch"
];

function getWebLink(filePath)
{
	return `file://${Deno.hostname()==="chatsubo" ? path.join("/mnt/chatsubo", path.relative("/mnt", filePath)) : filePath}`.encodeURLPath().escapeHTML();
}

const DEXTEST_ROOT_DIR = await fileUtil.genTempPath(undefined, "_dextest");
const startTime = performance.now();
const SLOW_DURATION = xu.MINUTE*5;
const slowFiles = {};
const DATA_FILE_PATH = path.join("/mnt/dexvert/test", `${Deno.hostname()}.json`);
const SAMPLE_DIR_PATH_SRC = path.join(xu.dirname(import.meta), "sample", ...(argv.format ? [argv.format] : []));
const SAMPLE_DIR_ROOT_PATH = "/mnt/ram/dexvert/sample";
const SAMPLE_DIR_PATH = path.join(SAMPLE_DIR_ROOT_PATH, ...(argv.format ? [argv.format] : []));
const outputFiles = [];

await Deno.mkdir(SAMPLE_DIR_PATH, {recursive : true});

xlog.info`${printUtil.majorHeader("dexvert test").trim()}`;
xlog.info`${argv.record ? fg.pink("RECORDING") : "Testing"} format: ${argv.format || "all formats"}`;
xlog.info`Root testing dir: ${fg.deepSkyblue(getWebLink(DEXTEST_ROOT_DIR))}`;
xlog.info`Rsyncing sample files to RAM...`;
await runUtil.run("rsync", ["--delete", "-savL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

xlog.info`Loading test data and finding sample files...`;

const testData = xu.parseJSON(await fileUtil.readTextFile(DATA_FILE_PATH), {});

xlog.info`Finding sample files...`;
const sampleFilePaths = await fileUtil.tree(SAMPLE_DIR_PATH, {nodir : true, depth : 3-(argv.format ? argv.format.split("/").length : 0)});
sampleFilePaths.filterInPlace(sampleFilePath => !SUPPORTING_DIR_PATHS.some(v => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath).startsWith(v)));

if(argv.file)
	sampleFilePaths.filterInPlace(sampleFilePath => sampleFilePath.toLowerCase().endsWith(argv.file.toString().toLowerCase()));
xlog.info`Testing ${sampleFilePaths.length} sample files...`;

Object.keys(testData).subtractAll(sampleFilePaths.map(sampleFilePath => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath))).forEach(extraFilePath =>
{
	if(!argv.format || !argv.format.includes("/") || !extraFilePath.startsWith(path.join(argv.format, "/")) || argv.file)
		return;

	xlog.info`${fg.cyan("[") + xu.c.blink + fg.red("EXTRA") + fg.cyan("]")} file path detected: ${extraFilePath}`;
	if(argv.record)
		delete testData[extraFilePath];
});

const oldDataFormats = [];
let completed=0;
let completedMark=0;
let failCount=0;
const failures=[];
async function testSample(sampleFilePath)
{
	const startedAt = performance.now();
	const sampleSubFilePath = path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath);
	const diskFamily = sampleSubFilePath.split("/")[0];
	const diskFormat = sampleSubFilePath.split("/")[1];
	const diskFormatid = `${diskFamily}/${diskFormat}`;
	const tmpOutDirPath = path.join(DEXTEST_ROOT_DIR, diskFamily, diskFormat, path.basename(sampleFilePath), "out");
	await Deno.mkdir(tmpOutDirPath, {recursive : true});
	const logFilePath = path.join(path.dirname(tmpOutDirPath), "log.txt");
	const dexvertArgs = ["--logLevel=debug", `--logFile=${logFilePath}`, "--json"];
	if(typeof FORMAT_OS_HINT[diskFormatid]==="string")
		dexvertArgs.push(`--programFlag=osHint:${FORMAT_OS_HINT[diskFormatid]}`);
	else if(Object.isObject(FORMAT_OS_HINT[diskFormatid]) && FORMAT_OS_HINT[diskFormatid][path.basename(sampleFilePath)])
		dexvertArgs.push(`--programFlag=osHint:${FORMAT_OS_HINT[diskFormatid][path.basename(sampleFilePath)]}`);

	if(FORCE_FORMAT_AS.includes(diskFormatid))
		dexvertArgs.push(`--asFormat=${diskFormatid}`);
	dexvertArgs.push(sampleFilePath, tmpOutDirPath);

	const r = await runUtil.run("dexvert", dexvertArgs, {timeout : xu.MINUTE*15, timeoutSignal : "SIGKILL", killChildren : true});
	const resultFull = xu.parseJSON(r.stdout, {});

	function handleComplete()
	{
		const duration = performance.now()-startedAt;
		if(duration>=SLOW_DURATION)
			slowFiles[sampleSubFilePath] = duration;

		// If we have more than 60 files we are testing, show progress every 10%
		if(sampleFilePaths.length>60)
		{
			completed++;
			const newMark = Math.floor((completed/sampleFilePaths.length)*10);
			if(newMark>completedMark)
			{
				completedMark = newMark;
				xu.stdoutWrite(fg.yellow(`${completedMark}0%`));
			}
		}
	}
	function fail(msg)
	{
		failCount++;

		failures.push(`${fg.cyan("[")}${xu.c.blink + fg.red("FAIL")}${fg.cyan("]")} ${xu.c.bold + sampleSubFilePath} ${xu.c.reset + msg}\n       ${fg.deepSkyblue(getWebLink(path.dirname(tmpOutDirPath)))}`);
		xu.stdoutWrite(xu.c.blink + fg.red("F"));
		if(argv.liveErrors)
			xlog.info`\n${failures.at(-1)}`;
		if(argv.report && !argv.record)
			outputFiles.push(...resultFull?.created?.files?.output?.map(v => v.absolute) || []);

		handleComplete();
	}

	async function pass(c)
	{
		xu.stdoutWrite(c);
		await fileUtil.unlink(logFilePath);

		if(argv.report && !argv.record)
			outputFiles.push(...resultFull?.created?.files?.output?.map(v => v.absolute) || []);
		else
			await fileUtil.unlink(tmpOutDirPath, {recursive : true});

		handleComplete();
	}

	if(!resultFull)
	{
		if(argv.record)
		{
			testData[sampleSubFilePath] = false;
			return await pass(fg.red(`${xu.c.blink}r`));	// blinking red 'r' === no results found
		}

		if(testData[sampleSubFilePath]===false)
			return pass(fg.whiteDim("."));

		return await fail(`${fg.pink("No result returned")} ${xu.bracket(`stderr: ${r.stderr.trim()}`)} ${xu.bracket(`stdout: ${r.stdout.trim()}`)} ${fg.deepSkyblue("but expected")} ${xu.inspect(testData[sampleSubFilePath]).squeeze()}`);
	}
	
	const result = {};
	result.processed = resultFull.processed;
	if(resultFull?.created?.files?.output?.length)
	{
		const misingFiles = (await resultFull.created.files.output.parallelMap(async ({absolute}) => ((await fileUtil.exists(absolute)) ? false : absolute))).filter(v => !!v);
		if(misingFiles.length>0)
			return await fail(`Some reported output files are missing from disk: ${misingFiles.join(" ")}`);

		result.files = Object.fromEntries(await resultFull.created.files.output.parallelMap(async ({rel, size, absolute, ts}) => [rel, {size, ts, sum : await hashUtil.hashFile("SHA-1", absolute)}]));
	}
	result.meta = resultFull?.phase?.meta || {};
	if(resultFull?.phase)
	{
		result.family = resultFull.phase.family;
		result.format = resultFull.phase.format;

		if(resultFull.phase.converter)
			result.converter = resultFull.phase.converter.split("[")[0];	// don't record any flags passed, they can be variable per running (bchunk cueFilePath for example)
	}
	
	if(argv.record)
	{
		if(testData?.[sampleSubFilePath]?.inputMeta)
			delete testData[sampleSubFilePath].inputMeta;

		testData[sampleSubFilePath] = result;
		return await pass(!resultFull?.created?.files?.output?.length ? fg.pink(`${xu.c.blink}r`) : fg.green("r"));		// blinking pink 'r' === no files found
	}

	if(!Object.hasOwn(testData, sampleSubFilePath))
		return await fail(`No test data for this file: ${xu.inspect(result).squeeze()}`);

	const prevData = testData[sampleSubFilePath];
	if(prevData.processed!==result.processed)
		return fail(`Expected processed to be ${fg.orange(prevData.processed)}${prevData.processed && prevData.converter ? ` ${xu.paren(prevData.converter)}` : ""} but got ${fg.orange(result.processed)}`);

	const allowFamilyMismatch = (DISK_FAMILY_FORMAT_MAP.some(([regex, mapToFamily]) => regex.test(sampleFilePath) && (mapToFamily===true || mapToFamily===result.family)));
	const allowFormatMismatch = (DISK_FAMILY_FORMAT_MAP.some(([regex, , mapToFormat]) => regex.test(sampleFilePath) && (mapToFormat===true || mapToFormat===result.format)));

	if(!result.processed)
	{
		if(!resultFull.ids.some(id => id.formatid===diskFormat) && !UNPROCESSED_ALLOW_NO_IDS.includes(`${diskFamily}/${diskFormat}`) && (!allowFamilyMismatch || !allowFormatMismatch))
			return await fail(`Processed is false (which was expected), but no id detected matching: ${diskFormat}`);

		return await pass(fg.fogGray("."));
	}

	if(!prevData.format)
		oldDataFormats.pushUnique(diskFormat);

	if(result.family && result.family!==diskFamily && !allowFamilyMismatch)
		return await fail(`Disk family ${fg.orange(diskFamily)} does not match processed family ${result.family}`);

	if(result.format && result.format!==diskFormat && !allowFormatMismatch)
		return await fail(`Disk format ${fg.orange(diskFormat)} does not match processed format ${result.format}`);

	if(prevData.files && !result.files)
		return await fail(`Expected to have ${fg.yellow(Object.keys(prevData.files).length)} files but found ${fg.yellow(0)} instead`);

	if(!prevData.files && result.files)
		return await fail(`Expected to have ${fg.yellow(0)} files but found ${fg.yellow(Object.keys(result.files).length)} instead`);

	if(result.files)
	{
		const diffFiles = diffUtil.diff(Object.keys(prevData.files).sortMulti(v => v), Object.keys(result.files).sortMulti(v => v));
		const diffFilesAllowed = FLEX_DIFF_FILES.some(regex => regex.test(sampleFilePath));
		if(diffFiles?.length && !SINGLE_FILE_DYNAMIC_NAMES.includes(diskFormatid) && !diffFilesAllowed)
			return await fail(`Created files are different: ${diffFiles}`);

		let allowedSizeDiff = (FLEX_SIZE_FORMATS?.[result.family]?.[result.format] || FLEX_SIZE_FORMATS?.[result.family]?.["*"] || 0);
		allowedSizeDiff = Math.max(allowedSizeDiff, (FLEX_SIZE_PROGRAMS?.[resultFull?.phase?.ran?.at(-1)?.programid] || 0));
		allowedSizeDiff = Math.max(allowedSizeDiff, (FLEX_SIZE_PROGRAMS?.[resultFull?.phase?.ran?.at(0)?.programid] || 0));

		// first make sure the files are the same
		for(const [name, {size, sum}] of Object.entries(result.files))
		{
			if(IGNORE_SIZE_FILEPATHS.some(re => re.test(name)))
				continue;

			const prevFile = SINGLE_FILE_DYNAMIC_NAMES.includes(diskFormatid) ? Object.values(prevData.files)[0] : prevData.files[name];
			if(!prevFile)	// can happen if FLEX_DIFF_FILES matches for this format/file
				continue;

			const sizeDiff = 100*(1-((prevFile.size-Math.abs(size-prevFile.size))/prevFile.size));

			const allowedFileSizeDiff = Math.max(FLEX_SIZE_FORMATS?.[result.family]?.[`*:${path.extname(name)}`] || allowedSizeDiff, allowedSizeDiff);
			if(sizeDiff!==0 && sizeDiff>allowedFileSizeDiff)
				return await fail(`Created file ${fg.peach(name)} differs in size by ${fg.yellow(sizeDiff.toFixed(2))}% (allowed ${fg.yellowDim(allowedFileSizeDiff)}%) Expected ${fg.yellow(prevFile.size.bytesToSize())} but got ${fg.yellow(size.bytesToSize())}`);

			if(allowedFileSizeDiff===0 && prevFile.sum!==sum)
				return await fail(`Created file ${fg.peach(name)} SHA1 sum differs!`);
		}

		// Now check timestamps
		for(const [name, {ts}] of Object.entries(result.files))
		{
			const prevFile = SINGLE_FILE_DYNAMIC_NAMES.includes(diskFormatid) ? Object.values(prevData.files)[0] : prevData.files[name];
			if(!prevFile)	// can happen if FLEX_DIFF_FILES matches for this format/file
				continue;

			const tsDate = new Date(ts);
			const prevDate = typeof prevFile.ts==="string" ? dateParse(prevFile.ts, "yyyy-MM-dd") : new Date(prevFile.ts || Date.now());
			if(tsDate.getFullYear()<2020 && prevDate.getFullYear()>=2020)
				return await fail(`Created file ${fg.peach(name)} ts was not expected to be old, but got old ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}`);

			if(prevDate.getFullYear()<2020 && Math.abs(tsDate.getTime()-prevDate.getTime())>xu.DAY)
				return await fail(`Created file ${fg.peach(name)} ts was expected to be ${fg.orange(dateFormat(prevDate, "yyyy-MM-dd"))} but got ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}`);
		}
	}

	if(prevData.family && result.family!==prevData.family)
		return await fail(`Expected to have family ${fg.orange(prevData.family)} but got ${result.family}`);

	if(prevData.format && result.format!==prevData.format && !allowFormatMismatch)
		return await fail(`Expected to have format ${fg.orange(prevData.format)} but got ${result.format}`);

	if(prevData.meta)
	{
		if(!result.meta)
			return fail(`Expected to have meta ${xu.inspect(prevData.meta).squeeze()} but have none`);

		const objDiff = diffUtil.diff(prevData.meta, result.meta);
		if(objDiff.length>0)
			return fail(`Meta different: ${objDiff.squeeze()}`);
	}
	else if(result.meta && Object.keys(result.meta).length>0)
	{
		return fail(`Expected no meta but got ${xu.inspect(result.meta).squeeze()} instead`);
	}

	if(prevData.converter && !result.converter)
		return await fail(`Expected converter ${fg.orange(prevData.converter)} but did not get one`);

	if(!prevData.converter && result.converter)
		return await fail(`Expected no converter but instead got ${fg.orange(result.converter)}`);

	if(prevData.converter!==result.converter)
		return await fail(`Expected converter ${prevData.converter} but instead got ${fg.orange(result.converter)}`);

	return await pass(fg.white("·"));
}

await sampleFilePaths.shuffle().parallelMap(testSample, navigator.hardwareConcurrency);

xlog.info``;	// gets us out of the period stdoud section onto a new line

if(failures.length>0)
	xlog.info`\n${failures.sortMulti().join("\n")}`;

async function writeOutputHTML()
{
	await Deno.writeTextFile("/mnt/ram/tmp/testdexvert.html", `
<html>
	<head>
		<meta charset="UTF-8">
		<title>${argv.format.escapeHTML() || "ALL FILES"}</title>
		<style>
			body, html
			{
				background-color: #1a1a1a;
				color: #ccc;
				font-family: "Terminus (TTF)";
			}

			a, a:visited
			{
				color: #8585ff;
			}

			img
			{
				padding: 5px;
				margin: 5px;
				float: left;
				background-color: grey;
				max-width: 350px;
				max-height: 350px;
			}

			.media
			{
				width: 47%;
				display: inline-block;
				text-align: right;
				line-height: 1.75em;
				margin-bottom: 0.25em;
			}

			.media label
			{
				vertical-align: top;
			}

			.media video
			{
				width : 50%;
			}

			.media audio
			{
				height: 1.5em;
				width : 50%
			}

			blink
			{
				animation: 1s linear infinite condemned_blink_effect;
			}

			@keyframes condemned_blink_effect
			{
  				0% { visibility: hidden; }
  				50% { visibility: hidden; }
  				100% { visibility: visible; }
			}

			iframe
			{
				background-color: #aaa;
				margin: 5px;
				border: 0;
				width: 32%;
				height: 200px;
			}
		</style>
	</head>
	<body>
		${oldDataFormats.length>0 ? `<blink style="font-weight: bold; color: red;">HAS OLD DATA</blink> — ${oldDataFormats.map(v => v.decolor()).join(" ")}<br>` : ""}${outputFiles.length.toLocaleString()} files<br>
		${outputFiles.sortMulti([filePath => path.basename(filePath)]).map(filePath =>
	{
		const ext = path.extname(filePath);
		const filePathSafe = getWebLink(filePath);
		const relFilePath = path.relative(path.join(DEXTEST_ROOT_DIR, ...path.relative(DEXTEST_ROOT_DIR, filePath).split("/").slice(0, 2)), filePath);
		switch(ext.toLowerCase())
		{
			case ".jpg":
			case ".gif":
			case ".png":
			case ".webp":
			case ".svg":
				return `<img src="${filePathSafe}">`;

			case ".mp4":
				return `<span class="media"><label>${relFilePath.escapeHTML()}</label><video controls="" muted="" playsinline="" src="${filePathSafe}"></video></span>`;

			case ".wav":
			case ".mp3":
				return `<span class="media"><label>${relFilePath.escapeHTML()}</label><audio controls src="${filePathSafe}" loop></audio></span>`;
			
			case ".txt":
			case ".pdf":
			case ".html":
				return `<iframe src="${filePathSafe}"></iframe>`;
		}

		return `<a href="${filePathSafe}">${relFilePath.escapeHTML()}</a><br>`;
	}).join("")}
	</body>
</html>`);
	xlog.info`\nReport written to: ${getWebLink("/mnt/ram/tmp/testdexvert.html")}`;
}

if(argv.record)
	await Deno.writeTextFile(DATA_FILE_PATH, JSON.stringify(testData));

await runUtil.run("find", [DEXTEST_ROOT_DIR, "-type", "d", "-empty", "-delete"]);

xlog.info`\nElapsed time: ${((performance.now()-startTime)/xu.SECOND).secondsAsHumanReadable()}`;

xlog.info`\n${(sampleFilePaths.length-failCount).toLocaleString()} out of ${sampleFilePaths.length.toLocaleString()} ${fg.green("succeded")} (${Math.floor((((sampleFilePaths.length-failCount)/sampleFilePaths.length)*100))}%)${failCount>0 ? ` — ${failCount.toLocaleString()} ${fg.red("failed")} (${Math.floor(((failCount/sampleFilePaths.length)*100))}%)` : ""}`;	// eslint-disable-line max-len

if(Object.keys(slowFiles).length>0)
{
	const slowSorted = Object.entries(slowFiles).sortMulti([([, v]) => v], [true]).map(([k, v]) => `\t${fg.orange((v/xu.SECOND).secondsAsHumanReadable({short : true}).padStart(8, " "))} ${fg.cyan("==>")} ${k}`);
	xlog.info`\nSlow files (${Object.keys(slowFiles).length.toLocaleString()}):\n${slowSorted.join("\n")}`;
}

if(oldDataFormats.length>0)
	xlog.info`\n${xu.c.blink + xu.c.bold + fg.red("HAS OLD DATA - NEED TO RE-RECORD")} — ${oldDataFormats.join(" ")}`;

if(argv.report && !argv.record)
	await writeOutputHTML();
