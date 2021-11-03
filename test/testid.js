import {xu} from "xu";
import {cmdUtil, fileUtil, printUtil, runUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { delay } from "https://deno.land/std@0.111.0/async/mod.ts";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexvert identification for 1 or all formats",
	opts    :
	{
		format  : {desc : "Only test a sinlgle format: archive/zip", hasValue : true},
		verbose : {desc : "Show additional info when processing"},
		record  : {desc : "Take the results of the identifications and save them as future expected results"}
	}});

const startTime = performance.now();
const DATA_FILE_PATH = path.join(xu.dirname(import.meta), "data", "identify.json");
const SAMPLE_DIR_PATH_SRC = path.join(xu.dirname(import.meta), "sample", ...(argv.format ? [argv.format] : []));
const SAMPLE_DIR_ROOT_PATH = "/mnt/ram/dexvert/sample";
const SAMPLE_DIR_PATH = path.join(SAMPLE_DIR_ROOT_PATH, ...(argv.format ? [argv.format] : []));

await Deno.mkdir(SAMPLE_DIR_PATH, {recursive : true});
await runUtil.run("rsync", ["--delete", "-avL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

printUtil.majorHeader("Identification Test");
xu.log`Loading test data and finding sample files...`;

const testData = xu.parseJSON(await fileUtil.readFile(DATA_FILE_PATH));
const sampleFilePaths = await fileUtil.tree(SAMPLE_DIR_PATH);

xu.log`Testing ${sampleFilePaths.length} sample files...`;

Object.keys(testData).subtractAll(sampleFilePaths.map(sampleFilePath => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath))).forEach(extraFilePath =>
{
	if(!argv.format || !extraFilePath.startsWith(path.join(argv.format, "/")))
		return;

	xu.log`${xu.cf.fg.cyan("[") + xu.c.blink + xu.cf.fg.red("EXTRA") + xu.cf.fg.cyan("]")} file path detected: ${extraFilePath}`;
	if(argv.record)
		delete testData[extraFilePath];
});

let passChain=0;
async function testSample(sampleFilePath)
{
	const sampleSubFilePath = path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath);
	const r = await runUtil.run("dexid", ["--json", sampleFilePath]);
	const ids = xu.parseJSON(r.stdout);
	
	function fail(msg)
	{
		xu.log`${passChain>0 ? "\n" : ""}${xu.cf.fg.cyan("[")}${xu.c.blink + xu.cf.fg.red("FAIL")}${xu.cf.fg.cyan("]")} ${xu.c.bold + sampleSubFilePath} ${xu.cf.fg.orange(msg)}`;
		if(passChain>0)
			passChain = 0;
	}

	function pass(c=".")
	{
		xu.stdoutWrite(c);
		passChain++;
	}

	function colorizeid(id)
	{
		return `${xu.cf.fg.deepSkyblue(id.magic)} ${xu.cf.fg.white(id.confidence)} ${xu.cf.fg.peach(id.matchType)} ${xu.cf.fg.yellow(id.family)}${xu.cf.fg.cyan("/")}${xu.cf.fg.yellowDim(id.formatid)}`;
	}

	if(!ids)
		return fail(`No id results returned ${r.stderr}`);

	ids.filterInPlace(id =>
	{
		if(id.from!=="dexvert")
			return false;

		delete id.extensions;
		delete id.from;
		delete id.unsupported;

		return true;
	});

	if(argv.record)
	{
		testData[sampleSubFilePath] = ids;
		return pass("r");
	}

	if(!Object.hasOwn(testData, sampleSubFilePath))
		return fail(`No test data for this file: ${xu.cf.fg.cyan("[")}${ids.map(colorizeid).join(xu.cf.fg.cyan("] ["))}${xu.cf.fg.cyan("]")}`);
	
	for(const id of ids)
	{
		const previd = testData[sampleSubFilePath].find(v => v.formatid===id.formatid);
		if(!previd)
			return fail(`New identification detected: ${colorizeid(id)}`);
		else if(previd.confidence!==id.confidence)
			return fail(`Confidence level changed for ${xu.cf.fg.white(id.formatid) + xu.c.fg.orange} was ${xu.cf.fg.white(previd.confidence) + xu.c.fg.orange} and now ${xu.cf.fg.white(id.confidence)}`);
	}

	for(const previd of testData[sampleSubFilePath])
	{
		const id = ids.find(v => v.formatid===previd.formatid);
		if(!id)
			return fail(`Previous identification not detected: ${colorizeid(previd)}`);
	}

	return pass(".");
}

await sampleFilePaths.shuffle().parallelMap(testSample, navigator.hardwareConcurrency);

if(argv.record)
	await fileUtil.writeFile(DATA_FILE_PATH, JSON.stringify(testData));

//testUtil.logFinish();
xu.log`\nElapsed time: ${((performance.now()-startTime)/xu.SECOND).secondsAsHumanReadable()}`;
