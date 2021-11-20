import {xu, fg} from "xu";
import {cmdUtil, fileUtil, printUtil, runUtil} from "xutil";
import {Identification} from "../src/Identification.js";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexvert identification for 1 or all formats",
	opts    :
	{
		format  : {desc : "Only test a sinlgle format: archive/zip", hasValue : true},
		record  : {desc : "Take the results of the identifications and save them as future expected results"}
	}});

const startTime = performance.now();
const DATA_FILE_PATH = path.join(xu.dirname(import.meta), "data", "identify.json");
const SAMPLE_DIR_PATH_SRC = path.join(xu.dirname(import.meta), "sample", ...(argv.format ? [argv.format] : []));
const SAMPLE_DIR_ROOT_PATH = "/mnt/ram/dexvert/sample";
const SAMPLE_DIR_PATH = path.join(SAMPLE_DIR_ROOT_PATH, ...(argv.format ? [argv.format] : []));

await Deno.mkdir(SAMPLE_DIR_PATH, {recursive : true});
await runUtil.run("rsync", ["--delete", "-avL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

console.log(printUtil.majorHeader("Identification Test"));
xu.log`Loading test data and finding sample files...`;

const testData = xu.parseJSON(await fileUtil.readFile(DATA_FILE_PATH));
const sampleFilePaths = await fileUtil.tree(SAMPLE_DIR_PATH);

xu.log`Testing ${sampleFilePaths.length} sample files...`;

Object.keys(testData).subtractAll(sampleFilePaths.map(sampleFilePath => path.relative(SAMPLE_DIR_ROOT_PATH, sampleFilePath))).forEach(extraFilePath =>
{
	if(!argv.format || !extraFilePath.startsWith(path.join(argv.format, "/")))
		return;

	xu.log`${fg.cyan("[") + xu.c.blink + fg.red("EXTRA") + fg.cyan("]")} file path detected: ${extraFilePath}`;
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
		xu.log`${passChain>0 ? "\n" : ""}${fg.cyan("[")}${xu.c.blink + fg.red("FAIL")}${fg.cyan("]")} ${xu.c.bold + sampleSubFilePath} ${fg.orange(msg)}`;
		if(passChain>0)
			passChain = 0;
	}

	function pass(c=".")
	{
		xu.stdoutWrite(c);
		passChain++;
	}

	if(!ids)
		return fail(`No id results returned ${r.stderr}`);

	ids.mapInPlace(id => Identification.create(id)).filterInPlace(id =>
	{
		if(id.from!=="dexvert")
			return false;

		delete id.extensions;
		delete id.unsupported;

		return true;
	});

	if(argv.record)
	{
		testData[sampleSubFilePath] = ids;
		return pass("r");
	}

	if(!Object.hasOwn(testData, sampleSubFilePath))
		return fail(`No test data for this file`);
	
	for(const id of ids)
	{
		const previd = testData[sampleSubFilePath].find(v => v.formatid===id.formatid);
		if(!previd)
			return fail(`New identification detected: ${id.pretty()}`);
		else if(previd.confidence!==id.confidence)
			return fail(`Confidence level changed for ${fg.white(id.formatid) + xu.c.fg.orange} was ${fg.white(previd.confidence) + xu.c.fg.orange} and now ${fg.white(id.confidence)}`);
	}

	for(const previd of testData[sampleSubFilePath])
	{
		const id = ids.find(v => v.formatid===previd.formatid);
		if(!id)
			return fail(`Previous identification not detected: ${Identification.create(previd).pretty()}`);
	}

	return pass(".");
}

await sampleFilePaths.shuffle().parallelMap(testSample, navigator.hardwareConcurrency);

if(argv.record)
	await fileUtil.writeFile(DATA_FILE_PATH, JSON.stringify(testData));

//testUtil.logFinish();
xu.log`\nElapsed time: ${((performance.now()-startTime)/xu.SECOND).secondsAsHumanReadable()}`;
