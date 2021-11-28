/* eslint-disable camelcase, prefer-named-capture-group */
import {xu, fg} from "xu";
import {cmdUtil, fileUtil, printUtil, runUtil, hashUtil, diffUtil} from "xutil";
import {path, dateFormat, dateParse} from "std";
import {formats} from "../src/format/formats.js";

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

const FLEX_SIZE_PROGRAMS =
{
	// Produces slightly different PNG output each time it's ran. Probably meta data somewhere, but didn't research it much
	darktable_cli : 0.1
};

const FLEX_SIZE_FORMATS =
{
	image :
	{
		// Each iteration generates different clippath ids, sigh.
		dxf : 1,

		// each running produces slightly different output, not sure why
		lottie      : 1,
		rekoCardset : 1,

		// Takes a screenshot or a framegrab which can differ slightly on each run
		fractalImageFormat : 7,
		naplps             : 20,
		threeDCK           : 10,

		// TODO TEMPROARY due to bug in abydos
		avatar         : 20,
		cebraText      : 20,
		mrgSystemsText : 20,
		softelText     : 20
	}
};

// Regex is matched against the sample file tested and the second item is the format to allow to match to or true to allow any format
const DISK_FORMAT_MAP =
[
	// These formats share generic .ext only, no magic matches
	[/image\/artistByEaton\/BLINKY\.ART$/, "asciiArtEditor"],
	[/image\/gfaArtist\/.+$/, "asciiArtEditor"],
	[/image\/pfsFirstPublisher\/.+$/, "artDirector"],

	// Supporting/AUX files
	[/image\/fig\/.+.(gif|jpg|xbm|xpm)$/, true]
];

const DEXTEST_ROOT_DIR = await fileUtil.genTempPath(undefined, "-dextest");
const startTime = performance.now();
const SLOW_DURATION = xu.MINUTE*3;
const fileDurations = {};
const DATA_FILE_PATH = path.join(xu.dirname(import.meta), "data", "process.json");
const SAMPLE_DIR_PATH_SRC = path.join(xu.dirname(import.meta), "sample", ...(argv.format ? [argv.format] : []));
const SAMPLE_DIR_ROOT_PATH = "/mnt/ram/dexvert/sample";
const SAMPLE_DIR_PATH = path.join(SAMPLE_DIR_ROOT_PATH, ...(argv.format ? [argv.format] : []));
const outputFiles = [];

await Deno.mkdir(SAMPLE_DIR_PATH, {recursive : true});

console.log(`${xu.c.clearScreen}./testdexvert ${Deno.args.join(" ")}`);
console.log(printUtil.majorHeader("dexvert test").trim());
xu.log`Root testing dir: ${DEXTEST_ROOT_DIR}`;
xu.log`Rsyncing sample files to RAM...`;
await runUtil.run("rsync", ["--delete", "-avL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

xu.log`Loading test data and finding sample files...`;

const testData = xu.parseJSON(await fileUtil.readFile(DATA_FILE_PATH));

xu.log`Finding sample files...`;
const sampleFilePaths = await fileUtil.tree(SAMPLE_DIR_PATH, {nodir : true});
xu.log`Found ${sampleFilePaths.length} sample files. Filtering those we don't have support for...`;
sampleFilePaths.filterInPlace(sampleFilePath => Object.hasOwn(formats, path.basename(path.dirname(sampleFilePath))));
if(argv.file)
	sampleFilePaths.filterInPlace(sampleFilePath => sampleFilePath.toLowerCase().endsWith(argv.file.toLowerCase()));
xu.log`Testing ${sampleFilePaths.length} sample files...`;

Object.keys(testData).subtractAll(sampleFilePaths.map(sampleFilePath => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath))).forEach(extraFilePath =>
{
	if(!argv.format || !argv.format.includes("/") || !extraFilePath.startsWith(path.join(argv.format, "/")) || argv.file)
		return;

	xu.log`${fg.cyan("[") + xu.c.blink + fg.red("EXTRA") + fg.cyan("]")} file path detected: ${extraFilePath}`;
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
	const sampleSubFilePath = path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath);
	const tmpOutDirPath = await fileUtil.genTempPath(path.join(DEXTEST_ROOT_DIR, path.basename(path.dirname(sampleFilePath))), `_${path.basename(sampleFilePath)}`);
	await Deno.mkdir(tmpOutDirPath, {recursive : true});
	const r = await runUtil.run("dexvert", [...(argv.debug ? ["--debug"] : []), "--json", sampleFilePath, tmpOutDirPath]);
	const resultFull = xu.parseJSON(r.stdout);

	function handleComplete()
	{
		// If we have more than 100 files we are testing, show progress every 10%
		if(sampleFilePaths.length>100)
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

		failures.push(`${fg.cyan("[")}${xu.c.blink + fg.red("FAIL")}${fg.cyan("]")} ${xu.c.bold + sampleSubFilePath} ${xu.c.reset + msg}`);
		xu.stdoutWrite(xu.c.blink + fg.red("F"));
		if(argv.liveErrors)
			console.log(`\n${failures.at(-1)}`);
		if(argv.report && !argv.record)
			outputFiles.push(...resultFull?.created?.files?.output?.map(v => v.absolute) || []);

		handleComplete();
	}

	async function pass(c)
	{
		xu.stdoutWrite(c);

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

		result.files = Object.fromEntries(await resultFull.created.files.output.parallelMap(async ({base, size, absolute, ts}) => [base, {size, ts, sum : await hashUtil.hashFile("sha1", absolute)}]));
	}
	result.meta = resultFull?.phase?.meta || {};
	if(resultFull?.phase)
	{
		result.family = resultFull.phase.family;
		result.format = resultFull.phase.format;

		if(resultFull.phase.converter)
			result.converter = resultFull.phase.converter;
	}
	
	if(testData?.[sampleSubFilePath]?.inputMeta)
		delete testData[sampleSubFilePath].inputMeta;
	
	if(argv.record)
	{
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
	if(!prevData.format)
		oldDataFormats.pushUnique(diskFormat);

	if(result.family && result.family!==diskFamily)
		return await fail(`Disk family ${fg.orange(diskFamily)} does not match processed family ${result.family}`);

	if(result.format && result.format!==diskFormat && !(DISK_FORMAT_MAP.some(([regex, mapTo]) => regex.test(sampleFilePath) && (mapTo===true || mapTo===result.format))))
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

		for(const [name, {size, sum, ts}] of Object.entries(result.files))
		{
			const prevFile = prevData.files[name];
			const sizeDiff = 100*(1-((prevFile.size-Math.abs(size-prevFile.size))/prevFile.size));

			if(sizeDiff!==0 && sizeDiff>allowedSizeDiff)
				return await fail(`Created file ${fg.peach(name)} differs in size by ${fg.yellow(sizeDiff.toFixed(2))}% (allowed ${fg.yellowDim(allowedSizeDiff)}%) Expected ${fg.yellow(prevFile.size.bytesToSize())} but got ${fg.yellow(size.bytesToSize())}`);

			if(allowedSizeDiff===0 && prevFile.sum!==sum)
				return await fail(`Created file ${fg.peach(name)} SHA1 sum differs!`);

			const tsDate = new Date(ts);
			const prevDate = typeof prevFile.ts==="string" ? dateParse(prevFile.ts, "yyyy-MM-dd") : new Date(prevFile.ts || Date.now());
			if(tsDate.getFullYear()<2020 && prevDate.getFullYear()>=2020)
				return await fail(`Created file ${fg.peach(name)} ts was not expected to be old, but got old ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}`);

			if(prevDate.getFullYear()<2020 && tsDate.getTime()!==prevDate.getTime() && Math.abs(tsDate.getTime()-prevDate.getTime())>xu.DAY)	// TODO remove the 1 day off check
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
	else if(result.meta && Object.keys(result.meta).length>0)
	{
		return fail(`Expected no meta but got ${xu.inspect(result.meta).squeeze()} instead`);
	}

	if(prevData.converter && !result.converter)
		return await fail(`Expected converter ${fg.orange(prevData.converter)} but did not get one`);

	if(!prevData.converter && result.converter)
		return await fail(`Expected no converter but instead got ${fg.orange(result.converter)}`);

	return await pass(fg.white("."));
}

await sampleFilePaths.shuffle().parallelMap(testSample, navigator.hardwareConcurrency);

console.log("");	// gets us out of the period stdoud section onto a new line

if(failures.length>0)
	console.log(`\n${failures.sortMulti().join("\n")}`);

async function writeOutputHTML()
{
	await fileUtil.writeFile("/mnt/ram/tmp/testdexvert.html", `
<html>
	<head>
		<title>${argv.format.escapeHTML() || "ALL FILES"}</title>
		<style>
			body, html
			{
				background-color: black;
				color: #ccc;
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
		</style>
	</head>
	<body>
		${oldDataFormats.length>0 ? `<blink style="font-weight: bold; color: red;">HAS OLD DATA</blink> — ${oldDataFormats.join(" ")}<br>` : ""}${outputFiles.length.toLocaleString()} files<br>
		${outputFiles.map(filePath =>
	{
		const ext = path.extname(filePath);
		const filePathSafe = `file://${filePath.escapeHTML()}`;
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
				return `<audio src="${filePathSafe}">`;
			
			case ".pdf":
				return `<iframe src="${filePathSafe}">`;
		}

		return `<a href="${filePathSafe}">${path.basename(filePath.escapeHTML())}</a>`;
	}).join("")}
	</body>
</html>`);
	xu.log`\nReport written to: file:///mnt/ram/tmp/testdexvert.html`;
}

if(argv.record)
	await fileUtil.writeFile(DATA_FILE_PATH, JSON.stringify(testData));

await runUtil.run("find", [DEXTEST_ROOT_DIR, "-type", "d", "-empty", "-delete"]);

xu.log`\nElapsed time: ${((performance.now()-startTime)/xu.SECOND).secondsAsHumanReadable()}`;

xu.log`\n${(sampleFilePaths.length-failCount)} out of ${sampleFilePaths.length} ${fg.green("succeded")} (${Math.floor((((sampleFilePaths.length-failCount)/sampleFilePaths.length)*100))}%)${failCount>0 ? ` — ${failCount} ${fg.red("failed")} (${Math.floor(((failCount/sampleFilePaths.length)*100))}%)` : ""}`;	// eslint-disable-line max-len

if(oldDataFormats.length>0)
	xu.log`\n${xu.c.blink + xu.c.bold + fg.red("HAS OLD DATA - NEED TO RE-RECORD")} — ${oldDataFormats.join(" ")}`;

if(argv.report && !argv.record)
	await writeOutputHTML();
