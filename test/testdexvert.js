/* eslint-disable camelcase, prefer-named-capture-group, unicorn/better-regex */
import {xu, fg} from "xu";
import {cmdUtil, fileUtil, printUtil, runUtil, hashUtil, diffUtil} from "xutil";
import {path, dateFormat, dateParse} from "std";
import {formats} from "../src/format/formats.js";

const xlog = xu.xLog();

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

const FLEX_SIZE_PROGRAMS =
{
	// Produces slightly different PNG output each time it's ran. Probably meta data somewhere, but didn't research it much
	darktable_cli : 0.1,

	// Can produce slightly different output each time
	doomMUS2mp3     : 2,
	soundFont2tomp3 : 10,
	xmp             : 2,
	zxtune123       : 2
};

const FLEX_SIZE_FORMATS =
{
	image :
	{
		// Each iteration generates different clippath ids, sigh.
		dxf : 1,

		// each running produces slightly different output, not sure why
		lottie           : 0.1,
		rekoCardset      : 0.1,
		windowsClipboard : 0.1,

		// Takes a screenshot or a framegrab which can differ slightly on each run
		fractalImageFormat : 7,
		naplps             : 20,
		threeDCK           : 10
	},
	music :
	{
		// sidplay generates different wavs each time, it
		sid : 15
	}
};

// Regex is matched against the sample file tested and the second item is the family and third is the format to allow to match to or true to allow any family/format
const DISK_FAMILY_FORMAT_MAP =
[
	// These formats share generic .ext only, no magic matches
	[/image\/asciiArtEditor\/.+$/, "image", "gfaArtist"],
	[/image\/artistByEaton\/BLINKY\.ART$/, "image", "asciiArtEditor"],
	[/image\/gfaArtist\/.+$/, "image", "asciiArtEditor"],
	[/image\/pfsFirstPublisher\/.+$/, "image", "artDirector"],
	[/image\/petsciiSeq\/.+$/, "image", "stadPAC"],

	// Unsupported files that end up getting matched to other stuff
	[/other\/installShieldHDR\/.+\.hdr/i, "image", "radiance"],
	[/other\/microsoftChatCharacter\/armando.avb$/, "image", "tga"],

	// Supporting/AUX files
	[/image\/fig\/.+\.(gif|jpg|xbm|xpm)$/i, "image", true],
	[/image\/printMasterShape\/.+\.sdr$/i, "other", true],
	[/music\/pokeyNoise\/.+\.info$/i, "image", "info"],
	[/music\/tfmx\/smpl\..+$/i, true, true],
	[/other\/pogNames\/.+\.pog$/i, "image", true],
	[/other\/printMasterShapeNames\/.+\.shp$/i, "image", true]
];

// Normally if a file is unprocessed, I at least require an id to the disk family/format, but some files can't even be matched to a format due to the generality of the format
const UNPROCESSED_ALLOW_NO_IDS =
[
	"image/bbcDisplayRAM",
	"image/teletext",
	"music/richardJoseph"
];

const DEXTEST_ROOT_DIR = await fileUtil.genTempPath(undefined, "_dextest");
const startTime = performance.now();
const SLOW_DURATION = xu.MINUTE*3;
const slowFiles = [];
const DATA_FILE_PATH = path.join(xu.dirname(import.meta), "data", "process.json");
const SAMPLE_DIR_PATH_SRC = path.join(xu.dirname(import.meta), "sample", ...(argv.format ? [argv.format] : []));
const SAMPLE_DIR_ROOT_PATH = "/mnt/ram/dexvert/sample";
const SAMPLE_DIR_PATH = path.join(SAMPLE_DIR_ROOT_PATH, ...(argv.format ? [argv.format] : []));
const outputFiles = [];

await Deno.mkdir(SAMPLE_DIR_PATH, {recursive : true});

xlog.info`${printUtil.majorHeader("dexvert test").trim()}`;
xlog.info`Root testing dir: ${fg.deepSkyblue(`file://${DEXTEST_ROOT_DIR}`)}`;
xlog.info`Rsyncing sample files to RAM...`;
await runUtil.run("rsync", ["--delete", "-avL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

xlog.info`Loading test data and finding sample files...`;

const testData = xu.parseJSON(await Deno.readTextFile(DATA_FILE_PATH), {});

xlog.info`Finding sample files...`;
const allSampleFilePaths = await fileUtil.tree(SAMPLE_DIR_PATH, {nodir : true, depth : 3-(argv.format ? argv.format.split("/").length : 0)});
allSampleFilePaths.filterInPlace(sampleFilePath => !SUPPORTING_DIR_PATHS.some(v => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath).startsWith(v)));

xlog.info`Found ${allSampleFilePaths.length} sample files. Filtering those we don't have support for...`;
const sampleFilePaths = allSampleFilePaths.filter(sampleFilePath =>
{
	const sampleRel = path.relative(path.join(SAMPLE_DIR_PATH, ".."), sampleFilePath);
	const sampleFormat = sampleRel.split("/")[argv.format.includes("/") ? 0 : 1];
	return Object.hasOwn(formats, sampleFormat);
});

if(allSampleFilePaths.subtractAll(sampleFilePaths).length>0)
	xlog.info`Skipping files we don't have formats for yet:\n\t${allSampleFilePaths.subtractAll(sampleFilePaths).join("\n\t")}`;

if(argv.file)
	sampleFilePaths.filterInPlace(sampleFilePath => sampleFilePath.toLowerCase().endsWith(argv.file.toLowerCase()));
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
	const tmpOutDirPath = await fileUtil.genTempPath(path.join(DEXTEST_ROOT_DIR, path.basename(path.dirname(sampleFilePath))), `_${path.basename(sampleFilePath)}`);
	await Deno.mkdir(tmpOutDirPath, {recursive : true});
	const logFilePath = await fileUtil.genTempPath(undefined, "testdexvert_log.txt");
	const dexvertArgs = ["--logLevel=debug", `--logFile=${logFilePath}`, "--json", sampleFilePath, tmpOutDirPath];
	const r = await runUtil.run("dexvert", dexvertArgs);
	const resultFull = xu.parseJSON(r.stdout, {});

	function handleComplete()
	{
		const duration = performance.now()-startedAt;
		if(duration>=SLOW_DURATION)
			slowFiles.push(sampleSubFilePath);

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

		failures.push(`${fg.cyan("[")}${xu.c.blink + fg.red("FAIL")}${fg.cyan("]")} ${xu.c.bold + sampleSubFilePath} ${xu.c.reset + msg}\n       ${fg.deepSkyblue(`file://${tmpOutDirPath}`)}\n       ${fg.deepSkyblue(`file://${logFilePath}`)}`);
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
			return await pass("r");
		}

		if(testData[sampleSubFilePath]===false)
			return pass(fg.white("."));

		return await fail(`${fg.pink("No result returned")} ${xu.bracket(`stderr: ${r.stderr.trim()}`)} ${xu.bracket(`stdout: ${r.stdout.trim()}`)} ${fg.deepSkyblue("but expected")} ${xu.inspect(testData[sampleSubFilePath]).squeeze()}`);
	}
	
	const result = {};
	result.processed = resultFull.processed;
	if(resultFull?.created?.files?.output?.length)
	{
		const misingFiles = (await resultFull.created.files.output.parallelMap(async ({absolute}) => ((await fileUtil.exists(absolute)) ? false : absolute))).filter(v => !!v);
		if(misingFiles.length>0)
			return await fail(`Some reported output files are missing from disk: ${misingFiles.join(" ")}`);

		result.files = Object.fromEntries(await resultFull.created.files.output.parallelMap(async ({rel, size, absolute, ts}) => [rel, {size, ts, sum : await hashUtil.hashFile("sha1", absolute)}]));
	}
	result.meta = resultFull?.phase?.meta || {};
	if(resultFull?.phase)
	{
		result.family = resultFull.phase.family;
		result.format = resultFull.phase.format;

		if(resultFull.phase.converter)
			result.converter = resultFull.phase.converter;
	}
	
	if(argv.record)
	{
		if(testData?.[sampleSubFilePath]?.inputMeta)
			delete testData[sampleSubFilePath].inputMeta;

		testData[sampleSubFilePath] = result;
		return await pass("r");
	}

	if(!Object.hasOwn(testData, sampleSubFilePath))
		return await fail(`No test data for this file: ${xu.inspect(result).squeeze()}`);

	const diskFamily = sampleSubFilePath.split("/")[0];
	const diskFormat = sampleSubFilePath.split("/")[1];

	const prevData = testData[sampleSubFilePath];
	if(prevData.processed!==result.processed)
		return fail(`Expected processed to be ${fg.orange(prevData.processed)} but got ${fg.orange(result.processed)}`);

	const allowFamilyMismatch = (DISK_FAMILY_FORMAT_MAP.some(([regex, mapToFamily]) => regex.test(sampleFilePath) && (mapToFamily===true || mapToFamily===result.family)));
	const allowFormatMismatch = (DISK_FAMILY_FORMAT_MAP.some(([regex, , mapToFormat]) => regex.test(sampleFilePath) && (mapToFormat===true || mapToFormat===result.format)));

	if(!result.processed)
	{
		if(!resultFull.ids.some(id => id.family===diskFamily && id.formatid===diskFormat) && !UNPROCESSED_ALLOW_NO_IDS.includes(`${diskFamily}/${diskFormat}`) && (!allowFamilyMismatch || !allowFormatMismatch))
			return await fail(`Processed is false (which was expected), but no id detected matching: ${diskFamily}/${diskFormat}`);

		return await pass(fg.white("."));
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
		if(diffFiles?.length)
			return await fail(`Created files are different: ${fg.orange(diffFiles)}`);

		let allowedSizeDiff = (FLEX_SIZE_FORMATS?.[result.family]?.[result.format] || 0);
		if(allowedSizeDiff===0)
			allowedSizeDiff = (FLEX_SIZE_PROGRAMS?.[resultFull?.phase?.ran?.at(-1)?.programid] || 0);

		// first make sure the files are the same
		for(const [name, {size, sum}] of Object.entries(result.files))
		{
			const prevFile = prevData.files[name];
			const sizeDiff = 100*(1-((prevFile.size-Math.abs(size-prevFile.size))/prevFile.size));

			if(sizeDiff!==0 && sizeDiff>allowedSizeDiff)
				return await fail(`Created file ${fg.peach(name)} differs in size by ${fg.yellow(sizeDiff.toFixed(2))}% (allowed ${fg.yellowDim(allowedSizeDiff)}%) Expected ${fg.yellow(prevFile.size.bytesToSize())} but got ${fg.yellow(size.bytesToSize())}`);

			if(allowedSizeDiff===0 && prevFile.sum!==sum)
				return await fail(`Created file ${fg.peach(name)} SHA1 sum differs!`);
		}

		// Now check timestamps
		for(const [name, {ts}] of Object.entries(result.files))
		{
			const prevFile = prevData.files[name];

			const tsDate = new Date(ts);
			const prevDate = typeof prevFile.ts==="string" ? dateParse(prevFile.ts, "yyyy-MM-dd") : new Date(prevFile.ts || Date.now());
			if(tsDate.getFullYear()<2020 && prevDate.getFullYear()>=2020)
				return await fail(`Created file ${fg.peach(name)} ts was not expected to be old, but got old ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}`);

			if(prevDate.getFullYear()<2020 && tsDate.getTime()!==prevDate.getTime() && Math.abs(tsDate.getTime()-prevDate.getTime())>xu.DAY*1.5)	// TODO remove the 1 day off check
				return await fail(`Created file ${fg.peach(name)} ts was expected to be ${fg.orange(dateFormat(prevDate, "yyyy-MM-dd"))} but got ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}`);
		}
	}

	if(prevData.family && result.family!==prevData.family)
		return await fail(`Expected to have family ${fg.orange(prevData.family)} but got ${result.family}`);

	if(prevData.format && result.format!==prevData.format)
		return await fail(`Expected to have format ${fg.orange(prevData.format)} but got ${result.format}`);

	if(prevData.meta)
	{
		if(!result.meta)
			return fail(`Expected to have meta ${xu.inspect(prevData.meta).squeeze()} but have none`);

		const objDiff = diffUtil.diff(prevData.meta, result.meta);
		if(objDiff.length>0)
			return fail(`Meta different: ${objDiff.squeeze()}`);
	}
	else if(prevData.inputMeta)
	{
		// TODO Remove once converted all
		const oldMeta = {};
		Object.values(prevData.inputMeta).forEach(o => Object.assign(oldMeta, o));
		if(Object.keys(oldMeta).length>0)
		{
			if(Object.keys(result.meta || {}).length===0)
				return fail(`Expected to find old meta but didn't get any. Old: ${xu.inspect(oldMeta)}`);
			
			const objDiff = diffUtil.diff(oldMeta, result.meta);
			if(objDiff.length>0)
				return fail(`OLD meta different from new: ${objDiff.squeeze()}`);
		}
	}
	else if(result.meta && Object.keys(result.meta).length>0)
	{
		return fail(`Expected no meta but got ${xu.inspect(result.meta).squeeze()} instead`);
	}

	if(prevData.converter && !result.converter)
		return await fail(`Expected converter ${fg.orange(prevData.converter)} but did not get one`);

	if(!prevData.converter && result.converter)
		return await fail(`Expected no converter but instead got ${fg.orange(result.converter)}`);

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

			.audio
			{
				width: 47%;
				display: inline-block;
				text-align: right;
				line-height: 1.75em;
				margin-bottom: 0.25em;
			}

			.audio label
			{
				vertical-align: top;
			}

			.audio audio
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
			}
		</style>
	</head>
	<body>
		${oldDataFormats.length>0 ? `<blink style="font-weight: bold; color: red;">HAS OLD DATA</blink> — ${oldDataFormats.map(v => v.decolor()).join(" ")}<br>` : ""}${outputFiles.length.toLocaleString()} files<br>
		${outputFiles.map(filePath =>
	{
		const ext = path.extname(filePath);
		const filePathSafe = `file://${filePath.escapeHTML()}`;
		const relFilePath = path.relative(path.join(DEXTEST_ROOT_DIR, ...path.relative(DEXTEST_ROOT_DIR, filePath).split("/").slice(0, 2)), filePath);
		switch(ext)
		{
			case ".jpg":
			case ".gif":
			case ".png":
			case ".webp":
			case ".svg":
				return `<img src="${filePathSafe}">`;
			
			case ".mp4":
				return `<video src="${filePathSafe}">`;

			case ".wav":
			case ".mp3":
				return `<span class="audio"><label>${relFilePath.escapeHTML()}</label><audio controls src="${filePathSafe}" loop></audio></span>`;
			
			case ".txt":
			case ".pdf":
				return `<iframe src="${filePathSafe}"></iframe>`;
		}

		return `<a href="${filePathSafe}">${relFilePath.escapeHTML()}</a><br>`;
	}).join("")}
	</body>
</html>`);
	xlog.info`\nReport written to: file:///mnt/ram/tmp/testdexvert.html`;
}

if(argv.record)
	await Deno.writeTextFile(DATA_FILE_PATH, JSON.stringify(testData));

await runUtil.run("find", [DEXTEST_ROOT_DIR, "-type", "d", "-empty", "-delete"]);

xlog.info`\nElapsed time: ${((performance.now()-startTime)/xu.SECOND).secondsAsHumanReadable()}`;

xlog.info`\n${(sampleFilePaths.length-failCount)} out of ${sampleFilePaths.length} ${fg.green("succeded")} (${Math.floor((((sampleFilePaths.length-failCount)/sampleFilePaths.length)*100))}%)${failCount>0 ? ` — ${failCount} ${fg.red("failed")} (${Math.floor(((failCount/sampleFilePaths.length)*100))}%)` : ""}`;	// eslint-disable-line max-len

if(slowFiles.length>0)
	xlog.info`\nSlow files (${slowFiles.length.toLocaleString()}):\n\t${slowFiles.join("\n\t")}`;

if(oldDataFormats.length>0)
	xlog.info`\n${xu.c.blink + xu.c.bold + fg.red("HAS OLD DATA - NEED TO RE-RECORD")} — ${oldDataFormats.join(" ")}`;

if(argv.report && !argv.record)
	await writeOutputHTML();
