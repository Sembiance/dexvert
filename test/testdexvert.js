/* eslint-disable camelcase, prefer-named-capture-group, unicorn/better-regex, sonarjs/no-empty-collection */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, printUtil, runUtil, hashUtil, diffUtil} from "xutil";
import {path, dateFormat, dateParse, base64Encode} from "std";
import {DEXRPC_HOST, DEXRPC_PORT} from "../src/server/dexrpc.js";
import {ANSIToHTML} from "thirdParty";
import {mkWeblink} from "./testUtil.js";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexvert conversions for 1 or all formats",
	opts    :
	{
		format     : {desc : "Only test a single format: archive/zip", hasValue : true},
		file       : {desc : "Only test sample files that end with this value, case insensitive.", hasValue : true},
		serial     : {desc : "Perform only 1 test at a time, this helps when debugging"},
		record     : {desc : "Take the results of the conversions and save them as future expected results"},
		json       : {desc : "Output results as JSON"},
		liveErrors : {desc : "Report errors live as they are detected instead of waiting until the end."},
		debug      : {desc : "Used temporarily when attempting to debug stuff"}
	}});

const xlog = new XLog("info", {alwaysEcho : !argv.json});
const testLogLines = [];
xlog.logger = line => testLogLines.push(line);

const outJSON = {};

// ensure if we have a format, it doesn't end with a forward slash, we count those to know how far to search deep in samples tree
argv.format = argv.format?.endsWith("/") ? argv.format.slice(0, -1) : argv.format;

// These formats should be skipped entirely for one reason or another
const SKIP_FORMATS =
[
	// these take AGES to extract, just WAY too long
	"archive/printArtist"
];

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
	"archive/iso" :
	{
		"OS_user_4.0.iso"                     : "nextstep",
		"Random-Dot 3D.iso"                   : "macintoshjp",
		"Bandai Visual CD-ROM Previews 3.iso" : "macintoshjp",
		"MAC100-1999-02.ISO"                  : "macintoshjp",
		"MACPEOPLE-1998-03-01.ISO"            : "macintoshjp",
		"MACPEOPLE-1999-02-01.ISO"            : "macintoshjp",
		"MACPEOPLE-2001-06-01.ISO"            : "macintoshjp",
		"MACUSER-MACBIN40A-1997-03.ISO"       : "macintoshjp"
	},
	"archive/sit" :
	{
		"SAM_4.5.1_Patcher_PPC Fol9633.sit" : "macintoshjp",
		"StuffIt Expander 6.0J ｲﾝｽﾄｰﾗ"      : "macintoshjp"
	},
	"archive/zip" : { "LamenDB.zip" : "macintoshjp" },
	"document/dbf"         :
	{
		"DEMO.ADB" : "fmtownsjpy",
		"DEMO.DBF" : "fmtownsjpy",
		"DEMO.HDB" : "fmtownsjpy"
	},
	"document/lotus123"    : { "_ç_[_ß_ñ_î_ñ.123" : "fmtownsjpy" },
	"document/rtf"         : { "シェアウェア登録メールサンプル.rtf" : "macintoshjp"},
	"document/wri"         : { "readme2.wri" : "fmtownsjpy"	},
	"image/macBinaryImage" : { "01-1-tiff-手塚莉絵" : "macintoshjp" },
	"image/printfox"       : "commodore",
	"image/spritePad"      : "commodore",
	"image/shfXLEdit"      : "commodore",
	"text/html"            : { "apple.html" : "macintoshjp" }
};

const FORMAT_PROGRAM_FLAG =
{
	"archive/iso" :
	{
		"PanicDisc (PANIC.COM).bin" : {bchunk : {forceMode1 : true}}
	}
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
	Email_Outlook_Message       : 1,
	fontforge                   : 2,
	fontographer                : 3,
	gimp                        : 5,
	sidplay2                    : 0.1,
	sndh2raw                    : 0.1,
	soundFont2tomp3             : 0.1,
	zxtune123                   : 0.1
};

// these formats have some meta data that can change per host or per upgradeand so we should just ignore it
const IGNORED_META_KEYS =
{
	image :
	{
		jng : ["colorCount"],
		pes : ["colorCount"]
	}
};

// these formats have supporting files that should be ignored
const SUPPORTING_FILES =
{
	archive :
	{
		pog : /\.pnm$/i
	},
	document :
	{
		hyperWriter : /\.hw[nt]$/i
	},
	image :
	{
		printMasterShape : /\.sdr$/i
	},
	other :
	{
		pogNames              : /\.pog$/i,
		printMasterShapeNames : /\.shp$/i
	}
};

const FLEX_SIZE_FORMATS =
{
	audio :
	{
		// MP3 generation changes very easily when packages are updated and on different hosts. almost always the same size, but the SHA1 sum differs
		"*:.mp3" : 0.1
	},
	archive :
	{
		// sometimes the SHA1 sum differs
		annaMarie             : 0.01,
		prehistorikCURArchive : 0.1,

		// different each time due to way it generates frames
		swf    : 25,
		swfEXE : 25,

		// different generation per host/version
		"amosMemoryBank:.mp3" : 1,
		"iso:.mp3"            : 1,
		"tnef:.pdf"           : 40,

		// the PBMs generated are different each time
		hypercard : 2,
		
		// these can differ a lot
		"rsrc:.png" : 999_999_999,
		"rsrc:.txt" : 1,

		// different PDF each time
		tnef : 0.1
	},
	document :
	{
		// these conversions sometimes differ WILDLY, haven't figured out why
		farallonReplica : 25,
		hlp             : 50,
		wildcatWCX      : 90,
		wordDoc         : 80,

		// very subtle differences each time, not sure why
		winampCompiledMakiScript : 0.1,

		// PDF generation has lots of embedded things that change from timestamps to unique generate id numbers and other meta data
		// Also different hosts generate different PDFs, no idea exactly why. Final output looks very similar, just slight formatting changes, not sure why, but eh.
		"*:.pdf" : 50,

		// HTML generation can change easily too
		"*:.html" : 1
	},
	image :
	{
		// each host can produce very slightly different output
		"*" : 0.1,
		"*:.gif" : 3,	// Animated GIFs even more so

		// Each iteration generates different clippath ids, sigh.
		dxf : 1,

		// each running sometimes produces slightly different output, not sure why, haven't investigated further
		ani              : 15,
		avsx             : 25,
		CADDrawDrawing   : 80,
		fuzzyBitmap      : 0.1,
		gimpBrush        : 20,
		lottie           : 0.1,
		lotusChart       : 5,
		odg              : 20,	// also differs per host
		pes              : 0.1,
		pgx              : 10,
		rekoCardset      : 0.1,
		ssiTLB           : 0.1,
		theDraw          : 0.1,
		windowsClipboard : 0.1,

		// differs depending on host
		avif     : 1,	// avifdec
		dwg      : 25,	// dwg2bmp
		macDraw  : 10,
		radiance : 1,	// pfsconvert
		x3f      : 0.1,	// dcraw

		// takes a screenshot or a framegrab which can differ slightly on each run
		fractalImageFormat : 7,
		naplps             : 20,
		theDrawCOM         : 5,
		threeDCK           : 20,

		// SVG generation (usually from soffice, but sometimes other) is tempermental, especially across hosts (macDraw, cmx, eps, freeHandDrawing, etc)
		"*:.svg" : 25
	},
	music :
	{
		// MP3 generation changes very easily when packages are updated and on different hosts
		"*:.mp3" : 25
	},
	video :
	{
		// MP4 generation changes very easily when packages are updated and on different hosts. almost always the same size, but the SHA1 sum differs
		"*:.mp4"           : 5,
		"movieSetter:.mp4" : 40,

		// these are screen recordings from DOSBox and can differ a good bit between each run
		disneyCFAST : 25,
		fantavision : 60,
		grasp       : 60
	}
};

// Specific files that vary in size each run
const IGNORE_SIZE_AND_CONVERTER_SRC_PATHS =
{
	image :
	{
		blizzardPicture : ["NightElfMaleNakedPelvisSkin00_07.blp"],	// blpngConverter crashes on some hosts for this file, dunno why
		cdr             : ["test.cdr"],		// on some hosts, scribus fails to process this file and things fallback to nconvert
		spectrum512S    : ["AI_R_010.SPS"],	// deark produces random garbage for this file, every time
		wpg             : ["test.wpg"]		// convert converts this to SVG incorrectly and is wildly different on different hosts
	},
	video :
	{
		wmv : ["Green Goblin Last Stand.asx"]	// varies up to like 70% on some hosts, not sure why
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
const FLEX_DIFF_FILES =
[
	// this specific file sometimes extracts a pict, sometimes a bmp, no idea why
	/archive\/rsrc\/Speedometer 4\.02\.rsrc$/,
	
	// not sure why, but sometimes I get a .txt sometimes I get a .pdf very weird
	/document\/wordDoc\/POWWOW\.DOC$/,
	
	// sometimes various .as scripts are exatracted, sometimes not
	/archive\/swf\/.+$/,
	/archive\/swfEXE\/.+$/,

	// on some hosts, scribus fails to process this file, not sure why
	/image\/cdr\/test\.cdr$/
];

// Regex is matched against the sample file tested and the second item is the family and third is the format to allow to match to or true to allow any family/format
const DISK_FAMILY_FORMAT_MAP =
[
	// Mis-classified by classify as garbage, but they do look like garbage, so we allow it and they get processed as something else instead
	[/image\/bmp\/WATER5\.BMP$/, "archive", true],
	[/image\/vzi\/X\.BIN$/, "image", "binaryText"],
	[/image\/vzi\/Y\.BIN$/, "image", "binaryText"],

	// These are actually mis-identified files, but I haven't come up with a good way to avoid it
	[/archive\/linuxEXTFilesystem\/2940-sbpcd-nonet\.img$/, "archive", "iso"],
	[/archive\/mdf\/R180 NG Media 1\.mdf$/, "archive", "iso"],
	[/archive\/rawPartition\/example\.img$/, "archive", "iso"],
	[/audio\/quickTimeAudio\/BOMBER_BGM$/, "archive", "macBinary"],
	[/audio\/quickTimeAudio\/Demo Music FileM$/, "archive", "macBinary"],
	[/image\/artStudio\/.*\.shp$/, "image", "loadstarSHP"],
	[/image\/binaryText\/goo-metroid\.bin$/, "image", "tga"],
	[/image\/hiEddi\/05$/, "image", "doodleC64"],
	[/image\/doodleAtari\/.*\.art$/i, "image", "asciiArtEditor"],
	[/image\/deskMatePaint\/set_mask\.pnt$/, "image", "prismPaint"],
	[/image\/paintPro\/SKI\.BIL/, "image", "colorSTar"],
	[/image\/pfsFirstPublisher\/DOG.ART$/, "image", "asciiArtEditor"],
	[/image\/rawBitmap\/MMAP14.RAW$/, "text", "txt"],
	[/image\/rawBitmap\/texture_logo.raw$/, "text", true],
	[/other\/iBrowseCookies\/.+/, "text", true],
	[/text\/rexx\/makeboot\.cmd$/, "text", "txt"],
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
	[/image\/artistByEaton\/BLINKY\.ART$/, "image", "gfaArtist"],
	[/image\/magicDraw\/.+$/, "image", "a2gsSHStar"],
	[/image\/petsciiSeq\/.+$/, "image", "stadPAC"],
	[/image\/pixelPerfect\/.+$/, "image", true],
	[/image\/pfsFirstPublisher\/.+$/, "image", "gfaArtist"],

	// Unsupported files that end up getting matched to other stuff
	[/audio\/aviAudio\/04mwwk00\.avi/, "archive", "riff"],
	[/audio\/dataShowSound\/.+/i, "text", true],
	[/document\/hancomWord\/.+/i, "archive", true],
	[/document\/hotHelpText\/.+\.txt$/i, "text", true],
	[/document\/imf\/.+/i, "text", true],
	[/document\/manPage\/glib\.man/i, "text", true],
	[/document\/microsoftPublisher\/.+/i, "archive", true],
	[/document\/pagePlus\/.+/i, "archive", true],
	[/document\/quarkXPress\/10_11X14\.qxd/, "text", true],
	[/document\/quarkXPress\/1_8\.5x11\.qxd report/, "text", true],
	[/document\/quarkXPress\/9_8\.5X14\.qxd report/, "text", true],
	[/document\/vCard\/.+/i, "text", true],
	[/executable\/dll\/emxlibc\.dll/i, "executable", "exe"],
	[/image\/a2Sprites\/.+/i, "text", true],
	[/image\/excelChart\/.+/i, "document", "xls"],
	[/image\/fiasco\/(b1|large|medium|small).fco/, "text", "txt"],
	[/image\/graphSaurus\/SNAT-2.SR5/, "image", "msxBASIC"],
	[/image\/jpegXL\/JXL\.jxl$/i, "text", true],
	[/image\/neoPaintPattern\/.+/i, "text", true],
	[/image\/teletextPackets\/TETRIS\.T42/, "text", "txt"],
	[/music\/renoise\/.+/i, "archive", "zip"],
	[/music\/tss\/.+/i, "text", true],
	[/other\/installShieldHDR\/.+\.hdr/i, "image", "radiance"],
	[/other\/microsoftChatCharacter\/armando.avb$/, "image", "tga"],
	[/poly\/povRay\/.+/i, "text", true],
	[/poly\/vrml\/.+/i, "text", true],
	[/poly\/ydl\/.+/i, "text", true],
	[/unsupported\/emacsCompiledLisp\/FILES\.ELC/i, "text", true],
	[/video\/acornReplayVideo\/(ducks2|bluegreen|parrot)/, "text", true],

	// Supporting/AUX files
	[/archive\/(cdi|iso)\/.+\.(cue|toc)$/i, "text", true],
	[/archive\/irixIDBArchive\/\.?(books|man|sw|$)/i, true, true],
	[/archive\/pog\/.+\.pnm$/i, "other", true],
	[/image\/fig\/.+\.(gif|jpg|xbm|xpm)$/i, "image", true],
	[/music\/pokeyNoise\/.+\.info$/i, "image", "info"],
	[/music\/tfmx\/smpl\..+$/i, true, true],
	[/other\/installShieldHDR\/.+\.(cab|hdr)/i, "archive", true]
];

// Normally if a file is unprocessed, I at least require an id to the disk family/format, but some files can't even be matched to a format due to the generality of the format or a specific filename that must match
const UNPROCESSED_ALLOW_NO_IDS =
[
	"archive/drRiptideArchive",
	"archive/irixIDBArchive",
	"archive/lostVikingsDAT",
	"archive/rar",
	"image/bbcDisplayRAM",
	"image/printfox",
	"image/teletext",
	"image/sprEd",
	"music/euphony",
	"music/msxBGM",
	"music/richardJoseph",
	"other/iBrowseCookies",
	"unsupported/binPatch"
];

const DEXTEST_ROOT_DIR = await fileUtil.genTempPath("/mnt/dexvert/test", "_dextest");
await Deno.mkdir(DEXTEST_ROOT_DIR, {recursive : true});

const NUM_WORKERS = Math.floor(navigator.hardwareConcurrency*0.60);
const startTime = performance.now();
const SLOW_DURATION = xu.MINUTE*10;
const slowFiles = {};
const DATA_FILE_PATH = path.join(import.meta.dirname, "testExpected.json");
const SAMPLE_DIR_PATH_SRC = path.join(import.meta.dirname, "sample", ...(argv.format ? [argv.format] : []));
const SAMPLE_DIR_ROOT_PATH = "/mnt/dexvert/sample";
const SAMPLE_DIR_PATH = path.join(SAMPLE_DIR_ROOT_PATH, ...(argv.format ? [argv.format] : []));
const outputFiles = [];

await Deno.mkdir(SAMPLE_DIR_PATH, {recursive : true});

xlog.info`${printUtil.majorHeader("dexvert test").trim()}`;
xlog.info`${argv.record ? fg.pink("RECORDING") : "Testing"} format: ${argv.format || "all formats"}`;
xlog.info`Root testing dir: ${fg.deepSkyblue(mkWeblink(DEXTEST_ROOT_DIR))}`;
xlog.info`Rsyncing sample files to scratch area...`;
await runUtil.run("rsync", ["--delete", "-savL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

xlog.info`Loading test data and finding sample files...`;

const testData = xu.parseJSON(await fileUtil.readTextFile(DATA_FILE_PATH), {});

xlog.info`Finding sample files...`;
const sampleFilePaths = await fileUtil.tree(SAMPLE_DIR_PATH, {nodir : true, depth : 3-(argv.format ? argv.format.split("/").length : 0)});
sampleFilePaths.filterInPlace(sampleFilePath => !SUPPORTING_DIR_PATHS.some(v => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath).startsWith(v)));

sampleFilePaths.filterInPlace(sampleFilePath =>
{
	const sampleSubFilePath = path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath);
	return !SUPPORTING_FILES?.[sampleSubFilePath.split("/")[0]]?.[sampleSubFilePath.split("/")[1]]?.test(sampleSubFilePath);
});

if(argv.file)
	sampleFilePaths.filterInPlace(sampleFilePath => sampleFilePath.toLowerCase().endsWith(argv.file.toString().toLowerCase()));

Object.keys(testData).subtractAll(sampleFilePaths.map(sampleFilePath => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath))).forEach(extraFilePath =>
{
	const sampleSubFilePath = path.relative(SAMPLE_DIR_ROOT_PATH, extraFilePath);
	if(!SUPPORTING_FILES?.[sampleSubFilePath.split("/")[0]]?.[sampleSubFilePath.split("/")[1]]?.test(sampleSubFilePath))
		return;

	if(!argv?.format?.includes("/") || !extraFilePath.startsWith(path.join(argv.format, "/")) || argv.file)
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
let workercbCount = 0;
const newSuccesses = [];
async function workercb({sampleFilePath, tmpOutDirPath, err, dexData})
{
	if(!sampleFilePath)
	{
		workercbCount++;
		return xlog.error`Failed to get sampleFilePath back from worker!`;
	}
	
	const startedAt = performance.now();
	const sampleSubFilePath = path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath);
	const diskFamily = sampleSubFilePath.split("/")[0];
	const diskFormat = sampleSubFilePath.split("/")[1];
	const diskFormatid = `${diskFamily}/${diskFormat}`;

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
				if(!argv.json)
					printUtil.stdoutWrite(fg.yellow(`${completedMark}0%`));
			}
		}

		workercbCount++;
	}

	function fail(msg)
	{
		failCount++;

		failures.push(`${fg.cyan("[")}${xu.c.blink + fg.red("FAIL")}${fg.cyan("]")} ${xu.c.bold + sampleSubFilePath} ${xu.c.reset + msg}\n`);
		if(!argv.json)
			printUtil.stdoutWrite(xu.c.blink + fg.red("F"));
		if(argv.liveErrors)
			xlog.info`\n${failures.at(-1)}`;
		if(!argv.record)
			outputFiles.push(...dexData?.created?.files?.output?.map(v => v.absolute) || []);

		handleComplete();
	}

	async function pass(c)
	{
		if(!argv.json)
			printUtil.stdoutWrite(c);

		if(!argv.record)
			outputFiles.push(...dexData?.created?.files?.output?.map(v => v.absolute) || []);
		else
			await fileUtil.unlink(path.dirname(tmpOutDirPath), {recursive : true});

		handleComplete();
	}

	function newSuccess()
	{
		if(!argv.json)
			printUtil.stdoutWrite(xu.c.blink + fg.green("N"));

		newSuccesses.push(`--format=${diskFormatid} --file='${path.relative(diskFormatid, sampleSubFilePath)}'`);

		if(!argv.record)
			outputFiles.push(...dexData?.created?.files?.output?.map(v => v.absolute) || []);

		handleComplete();
	}

	if(!dexData)
	{
		if(argv.record)
		{
			testData[sampleSubFilePath] = false;
			return await pass(fg.red(`${xu.c.blink}r`));	// blinking red 'r' === no results found
		}

		if(testData[sampleSubFilePath]===false)
			return pass(fg.whiteDim("."));

		return await fail(`${fg.pink("No dexData result returned")} ${fg.deepSkyblue("but expected")} ${printUtil.inspect(testData[sampleSubFilePath]).squeeze()} with err ${err}`);
	}

	const result = {};
	result.processed = dexData.processed;
	if(dexData?.created?.files?.output?.length)
	{
		const misingFiles = (await dexData.created.files.output.parallelMap(async ({absolute}) => ((await fileUtil.exists(absolute)) ? false : absolute))).filter(v => !!v);
		if(misingFiles.length>0)
			return await fail(`Some reported output files are missing from disk: ${misingFiles.join(" ")}`);

		result.files = Object.fromEntries(await dexData.created.files.output.parallelMap(async ({rel, size, absolute, ts}) => [rel, {size, ts, sum : await hashUtil.hashFile("SHA-1", absolute)}]));
	}
	result.meta = dexData?.phase?.meta || {};
	if(dexData?.phase)
	{
		result.family = dexData.phase.family;
		result.format = dexData.phase.format;

		if(dexData.phase.converter)
			result.converter = dexData.phase.converter.split("[")[0];	// don't record any flags passed, they can be variable per running (bchunk cueFilePath for example)
	}
	
	if(argv.record)
	{
		if(testData?.[sampleSubFilePath]?.inputMeta)
			delete testData[sampleSubFilePath].inputMeta;

		testData[sampleSubFilePath] = result;
		return await pass(!dexData?.created?.files?.output?.length ? fg.pink("r") : fg.green("r"));		// pink 'r' === no files found
	}

	if(!Object.hasOwn(testData, sampleSubFilePath))
		return result.processed ? await newSuccess() : await fail(`No test data for this file: ${printUtil.inspect(result).squeeze().innerTruncate(3000)}`);

	const prevData = testData[sampleSubFilePath];
	if(prevData.processed!==result.processed)
		return fail(`Expected processed to be ${fg.orange(prevData.processed)}${prevData.processed && prevData.converter ? ` ${xu.paren(prevData.converter)}` : ""} but got ${fg.orange(result.processed)}`);

	const allowFamilyMismatch = (DISK_FAMILY_FORMAT_MAP.some(([regex, mapToFamily]) => regex.test(sampleFilePath) && (mapToFamily===true || mapToFamily===result.family)));
	const allowFormatMismatch = (DISK_FAMILY_FORMAT_MAP.some(([regex, , mapToFormat]) => regex.test(sampleFilePath) && (mapToFormat===true || mapToFormat===result.format)));

	if(!result.processed)
	{
		if(!dexData.ids.some(id => id.formatid===diskFormat) && !UNPROCESSED_ALLOW_NO_IDS.includes(`${diskFamily}/${diskFormat}`) && (!allowFamilyMismatch || !allowFormatMismatch))
			return await fail(`Processed is false (which was expected), but no id detected matching: ${diskFormat}`);

		return await pass(fg.fogGray("."));
	}

	if(!prevData.format)
		oldDataFormats.pushUnique(diskFormat);

	const ignoreSizeAndConverter = IGNORE_SIZE_AND_CONVERTER_SRC_PATHS?.[result.family]?.[result.format]?.includes(path.basename(sampleFilePath));

	const converterMismatch = prevData.converter!==result.converter && !ignoreSizeAndConverter ? ` Also, expected converter ${prevData.converter} but instead got ${fg.orange(result.converter)}` : "";

	if(result.family && result.family!==diskFamily && !allowFamilyMismatch)
		return await fail(`Disk family ${fg.orange(diskFamily)} does not match processed family ${result.family}${converterMismatch}`);

	if(result.format && result.format!==diskFormat && !allowFormatMismatch)
		return await fail(`Disk format ${fg.orange(diskFormat)} does not match processed format ${result.format}${converterMismatch}`);

	if(prevData.files && !result.files)
		return await fail(`Expected to have ${fg.yellow(Object.keys(prevData.files).length)} files but found ${fg.yellow(0)} instead${converterMismatch}`);

	if(!prevData.files && result.files)
		return await fail(`Expected to have ${fg.yellow(0)} files but found ${fg.yellow(Object.keys(result.files).length)} instead${converterMismatch}`);

	if(result.files)
	{
		const diffFiles = diffUtil.diff(Object.keys(prevData.files).sortMulti(v => v), Object.keys(result.files).sortMulti(v => v));
		const diffFilesAllowed = FLEX_DIFF_FILES.some(regex => regex.test(sampleFilePath));
		if(diffFiles?.length && !SINGLE_FILE_DYNAMIC_NAMES.includes(diskFormatid) && !diffFilesAllowed)
			return await fail(`Created files are different: ${diffFiles.innerTruncate(3000)}${converterMismatch}`);

		let allowedSizeDiff = (FLEX_SIZE_FORMATS?.[result.family]?.[result.format] || FLEX_SIZE_FORMATS?.[result.family]?.["*"] || 0);
		allowedSizeDiff = Math.max(allowedSizeDiff, (FLEX_SIZE_PROGRAMS?.[dexData?.phase?.ran?.at(-1)?.programid] || 0));
		allowedSizeDiff = Math.max(allowedSizeDiff, (FLEX_SIZE_PROGRAMS?.[dexData?.phase?.ran?.at(0)?.programid] || 0));

		// first make sure the files are the same
		for(const [name, {size, sum}] of Object.entries(result.files))
		{
			if(ignoreSizeAndConverter)
				continue;

			if(IGNORE_SIZE_FILEPATHS.some(re => re.test(name)))
				continue;

			const prevFile = SINGLE_FILE_DYNAMIC_NAMES.includes(diskFormatid) ? Object.values(prevData.files)[0] : prevData.files[name];
			if(!prevFile)	// can happen if FLEX_DIFF_FILES matches for this format/file
				continue;

			const sizeDiff = 100*(1-((prevFile.size-Math.abs(size-prevFile.size))/prevFile.size));

			const allowedFileSizeDiff = Math.max(FLEX_SIZE_FORMATS?.[result.family]?.[`*:${path.extname(name)}`] || FLEX_SIZE_FORMATS?.[result.family]?.[`${result.format}:${path.extname(name)}`] || allowedSizeDiff, allowedSizeDiff);
			if(sizeDiff!==0 && sizeDiff>allowedFileSizeDiff)
				return await fail(`Created file ${fg.peach(name)} differs in size by ${fg[sizeDiff<5 ? "green" : (sizeDiff>70 ? "red" : "yellow")](sizeDiff.toFixed(2))}% (allowed ${fg.yellowDim(allowedFileSizeDiff)}%) Expected ${fg.yellow(prevFile.size.bytesToSize())} but got ${fg.yellow(size.bytesToSize())}${converterMismatch}`);

			if(allowedFileSizeDiff===0 && prevFile.sum!==sum)
				return await fail(`Created file ${fg.peach(name)} SHA1 sum differs, but file is the expected size.${converterMismatch}`);
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
				return await fail(`Created file ${fg.peach(name)} ts was not expected to be old, but got old ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}${converterMismatch}`);

			if(prevDate.getFullYear()<2020 && Math.abs(tsDate.getTime()-prevDate.getTime())>(xu.DAY*2))
				return await fail(`Created file ${fg.peach(name)} ts was expected to be ${fg.orange(dateFormat(prevDate, "yyyy-MM-dd"))} but got ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}${converterMismatch}`);
		}
	}

	if(prevData.family && result.family!==prevData.family)
		return await fail(`Expected to have family ${fg.orange(prevData.family)} but got ${result.family}${converterMismatch}`);

	if(prevData.format && result.format!==prevData.format && !allowFormatMismatch)
		return await fail(`Expected to have format ${fg.orange(prevData.format)} but got ${result.format}${converterMismatch}`);

	if(prevData.meta)
	{
		if(!result.meta)
			return fail(`Expected to have meta ${printUtil.inspect(prevData.meta).squeeze()} but have none${converterMismatch}`);

		for(const k of IGNORED_META_KEYS[result.family]?.[result.format] || IGNORED_META_KEYS[result.family]?.["*"] || [])
		{
			if(prevData.meta[k] && result.meta[k])
				prevData.meta[k] = result.meta[k];
		}

		const objDiff = diffUtil.diff(prevData.meta, result.meta);
		if(objDiff.length>0)
			return fail(`Meta different: ${objDiff.squeeze()}`);
	}
	else if(result.meta && Object.keys(result.meta).length>0)
	{
		return fail(`Expected no meta but got ${printUtil.inspect(result.meta).squeeze()} instead${converterMismatch}`);
	}

	if(prevData.converter && !result.converter)
		return await fail(`Expected converter ${fg.orange(prevData.converter)} but did not get one`);

	if(!prevData.converter && result.converter)
		return await fail(`Expected no converter but instead got ${fg.orange(result.converter)}`);

	if(converterMismatch?.length)
		return await fail(converterMismatch);

	return await pass(fg.white("·"));
}

xlog.info`Testing ${sampleFilePaths.length} sample files...`;
//pool.process(await sampleFilePaths.shuffle().parallelMap(async sampleFilePath =>
await sampleFilePaths.shuffle().parallelMap(async sampleFilePath =>
{
	const sampleSubFilePath = path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath);
	const diskFamily = sampleSubFilePath.split("/")[0];
	const diskFormat = sampleSubFilePath.split("/")[1];
	const diskFormatid = `${diskFamily}/${diskFormat}`;
	if(SKIP_FORMATS.includes(diskFormatid))
	{
		workercbCount++;
		return xlog.info`SKIPPING ${sampleSubFilePath} because it's format is in the skip list: ${diskFormatid}`;
	}

	const tmpOutDirPath = path.join(DEXTEST_ROOT_DIR, diskFamily, diskFormat, path.basename(sampleFilePath), "out");
	await Deno.mkdir(tmpOutDirPath, {recursive : true});

	const o = {op : "dexvert", inputFilePath : sampleFilePath, outputDirPath : tmpOutDirPath, logLevel : "info", prod : true, dexvertOptions : {programFlag : {}}};
	if(typeof FORMAT_OS_HINT[diskFormatid]==="string")
	{
		o.dexvertOptions.programFlag.osHint = {};
		o.dexvertOptions.programFlag.osHint[FORMAT_OS_HINT[diskFormatid]] = true;
	}
	else if(Object.isObject(FORMAT_OS_HINT[diskFormatid]) && FORMAT_OS_HINT[diskFormatid][path.basename(sampleFilePath)])
	{
		o.dexvertOptions.programFlag.osHint = {};
		o.dexvertOptions.programFlag.osHint[FORMAT_OS_HINT[diskFormatid][path.basename(sampleFilePath)]] = true;
	}
	if(Object.isObject(FORMAT_PROGRAM_FLAG[diskFormatid]) && FORMAT_PROGRAM_FLAG[diskFormatid][path.basename(sampleFilePath)])
		Object.assign(o.dexvertOptions.programFlag, FORMAT_PROGRAM_FLAG[diskFormatid][path.basename(sampleFilePath)]);
	if(FORCE_FORMAT_AS.includes(diskFormatid))
		o.dexvertOptions.asFormat = diskFormatid;

	if(argv.serial)
		xlog.info`Attempting file: ${sampleSubFilePath}`;
	const {r, logLines} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(o)}))?.json()), {});
	if(logLines?.length)
		await fileUtil.writeTextFile(path.join(path.dirname(tmpOutDirPath), "log.txt"), logLines.join("\n"));

	await workercb({sampleFilePath, tmpOutDirPath, dexData : r.json});
}, argv.serial ? 1 : Math.min(sampleFilePaths.length, NUM_WORKERS));

await xu.waitUntil(() => workercbCount===sampleFilePaths.length);

xlog.info``;	// gets us out of the period stdoud section onto a new line

if(failures.length>0)
	xlog.info`\n${failures.sortMulti().join("\n")}`;

if(newSuccesses.length>0)
{
	const recordNewSuccessesScriptFilePath = await fileUtil.genTempPath(DEXTEST_ROOT_DIR, ".sh");
	xlog.info`\n\n${newSuccesses.length.toLocaleString()} new successes. ${fg.pink("Execute to record")}: ${recordNewSuccessesScriptFilePath}`;
	await fileUtil.writeTextFile(recordNewSuccessesScriptFilePath, `#!/bin/bash
cd /mnt/compendium/DevLab/dexvert/test || exit
${newSuccesses.map(v => `./testdexvert --record ${v}`).join("\n")}
`);
	await runUtil.run("chmod", ["755", recordNewSuccessesScriptFilePath]);
}

async function writeOutputHTML()
{
	xlog.info`Generating HTML report...`;
	const a2html = new ANSIToHTML();
	const reportFilePath = path.join(DEXTEST_ROOT_DIR, "report.html");
	await fileUtil.writeTextFile(reportFilePath, `
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

			.embed
			{
				display: inline-block;
				width: 32%;
				margin-right: 10px;
				margin-bottom: 15px;
				text-align: center;
			}

			iframe
			{
				background-color: #aaa;
				border: 0;
				margin-top: 2px;
				width: 100%;
				height: 225px;
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

			.topRightInfo
			{
				position: absolute;
				right: 8px;
				top: 8px;
			}

			a
			{
				border: 0;
			}

			hr
			{
				clear: both;
			}

			model-viewer
			{
				display: inline-block;
				width: 350px;
				height: 350px;
				margin: 5px;
				float: left;
				border: 2px solid #555;
			}

			model-viewer:after
			{
				content: attr(title);
				color: #fff;
				text-shadow: 0 1px 2px rgba(0, 0, 0, 0.9), 0 -1px 2px rgba(0, 0, 0, 0.9), -1px 0 2px rgba(0, 0, 0, 0.9), 1px 0 2px rgba(0, 0, 0, 0.9);
				position: absolute;
				left: 0;
				top: 0;
			}
		</style>
	</head>
	<body>
		<script type="module">${await fileUtil.readTextFile("/mnt/compendium/DevLab/dexvert/test/model-viewer.min.js")}</script>
		${oldDataFormats.length>0 ? `<blink style="font-weight: bold; color: red;">HAS OLD DATA</blink> — ${oldDataFormats.map(v => v.decolor()).join(" ")}<br>` : ""}		
		${outputFiles.length.toLocaleString()} files<br>
		<span class="topRightInfo">formats: ${argv.format.escapeHTML() || "all formats"}</span>
		${(await outputFiles.sortMulti([filePath => path.basename(filePath)]).parallelMap(async filePath =>
	{
		const titleSafe = path.basename(filePath).escapeHTML();
		const ext = path.extname(filePath);
		const filePathSafe = mkWeblink(filePath);
		const relFilePath = path.relative(path.join(DEXTEST_ROOT_DIR, ...path.relative(DEXTEST_ROOT_DIR, filePath).split("/").slice(0, 2)), filePath);
		switch(ext.toLowerCase())
		{
			case ".jpg":
			case ".gif":
			case ".png":
			case ".webp":
			case ".svg":
				return `<a href="${filePathSafe}" title="${titleSafe}"><img src="${filePathSafe}"></a>`;

			case ".mp4":
				return `<span class="media" title="${titleSafe}"><label>${relFilePath.escapeHTML()}</label><video controls="" muted="" playsinline="" src="${filePathSafe}"></video></span>`;

			case ".wav":
			case ".mp3":
				return `<span class="media" title="${titleSafe}"><label>${relFilePath.escapeHTML()}</label><audio controls src="${filePathSafe}" loop></audio></span>`;
			
			case ".txt":
			case ".pdf":
			case ".html":
				return `<span class="embed"><a href="${filePathSafe}" title="${titleSafe}">${titleSafe}</a><br><iframe src="${filePathSafe}" title="${titleSafe}"></iframe></span>`;
			
			case ".glb":
				return `<model-viewer loading="lazy" title="${titleSafe}" interaction-prompt="none" camera-controls touch-action="none" src="data:model/gltf-binary;base64,${base64Encode(await Deno.readFile(filePath))}" shadow-intensity="0"></model-viewer>`;
		}

		return `<a href="${filePathSafe}">${relFilePath.escapeHTML()}</a><br>`;
	})).join("")}
	<hr>
	${testLogLines.flatMap(v => v.split("\n")).map(v => a2html.toHtml(v)).join("<br>").replaceAll("<br><br>", "<br>").replaceAll("<br><br>", "<br>").replaceAll("<br><br>", "<br>")}
	</body>
</html>`);
	xlog.info`\nReport written to: ${mkWeblink(reportFilePath)}`;
	outJSON.reportFilePath = reportFilePath;
}

if(argv.record)
	await fileUtil.writeTextFile(DATA_FILE_PATH, JSON.stringify(testData));

await runUtil.run("find", [DEXTEST_ROOT_DIR, "-type", "d", "-empty", "-delete"]);

outJSON.elapsed = performance.now()-startTime;
xlog.info`\nElapsed time: ${(outJSON.elapsed/xu.SECOND).secondsAsHumanReadable()}`;

outJSON.successPercentage = Math.floor((((sampleFilePaths.length-failCount)/sampleFilePaths.length)*100));
xlog.info`\n${(sampleFilePaths.length-failCount).toLocaleString()} out of ${sampleFilePaths.length.toLocaleString()} ${fg.green("succeded")} (${outJSON.successPercentage}%)${failCount>0 ? ` — ${failCount.toLocaleString()} ${fg.red("failed")} (${Math.floor(((failCount/sampleFilePaths.length)*100))}%)` : ""}`;
outJSON.sampleFileCount = sampleFilePaths.length;
outJSON.failCount = failCount;
outJSON.testLogLines = testLogLines;
outJSON.newSuccessesCount = newSuccesses.length;

if(Object.keys(slowFiles).length>0)
{
	const slowSorted = Object.entries(slowFiles).sortMulti([([, v]) => v], [true]).map(([k, v]) => `\t${fg.orange((v/xu.SECOND).secondsAsHumanReadable({short : true}).padStart(8, " "))} ${fg.cyan("==>")} ${k}`);
	xlog.info`\nSlow files (${Object.keys(slowFiles).length.toLocaleString()}):\n${slowSorted.join("\n")}`;
}

if(oldDataFormats.length>0)
	xlog.info`\n${xu.c.blink + xu.c.bold + fg.red("HAS OLD DATA - NEED TO RE-RECORD")} — ${oldDataFormats.join(" ")}`;

if(!argv.record && await fileUtil.exists(DEXTEST_ROOT_DIR))
	await writeOutputHTML();

if(argv.json)
	console.log(JSON.stringify(outJSON));
