import {xu, fg} from "xu";
import {cmdUtil, fileUtil, printUtil, runUtil, hashUtil, diffUtil} from "xutil";
import {path, dateFormat} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexvert conversions for 1 or all formats",
	opts    :
	{
		format  : {desc : "Only test a sinlgle format: archive/zip", hasValue : true},
		record  : {desc : "Take the results of the identifications and save them as future expected results"}
	}});

let startTime = performance.now();
const SLOW_DURATION = xu.MINUTE*3;
const fileDurations = {};
const DATA_FILE_PATH = path.join(xu.dirname(import.meta), "data", "process.json");
const SAMPLE_DIR_PATH_SRC = path.join(xu.dirname(import.meta), "sample", ...(argv.format ? [argv.format] : []));
const SAMPLE_DIR_ROOT_PATH = "/mnt/ram/dexvert/sample";
const SAMPLE_DIR_PATH = path.join(SAMPLE_DIR_ROOT_PATH, ...(argv.format ? [argv.format] : []));

await Deno.mkdir(SAMPLE_DIR_PATH, {recursive : true});
await runUtil.run("rsync", ["--delete", "-avL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

console.log(printUtil.majorHeader("Identification Test").trim());
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
	const tmpOutDirPath = await fileUtil.genTempPath(undefined, `test-${path.basename(path.dirname(sampleFilePath))}`);
	await Deno.mkdir(tmpOutDirPath);
	const r = await runUtil.run("dexvert", ["--json", sampleFilePath, tmpOutDirPath]);
	const resultFull = xu.parseJSON(r.stdout);

	function fail(msg)
	{
		xu.log`${passChain>0 ? "\n" : ""}${fg.cyan("[")}${xu.c.blink + fg.red("FAIL")}${fg.cyan("]")} ${xu.c.bold + sampleSubFilePath} ${xu.c.reset + msg}`;
		if(passChain>0)
			passChain = 0;
	}

	function pass(c=".")
	{
		xu.stdoutWrite(c);
		passChain++;
	}

	if(!resultFull)
		return fail(`No result returned ${r.stderr}`);
	
	const result = {};
	result.processed = resultFull.processed;
	if(resultFull?.created?.files?.output?.length)
		result.files = Object.fromEntries(await resultFull.created.files.output.parallelMap(async ({base, size, absolute, ts}) => [base, {size, ts, sum : await hashUtil.hashFile("sha1", absolute)}]));
	result.meta = resultFull?.phase?.meta || {};
	if(resultFull?.phase)
	{
		if(resultFull.phase.id)
		{
			result.family = resultFull.phase.id.family;
			result.formatid = resultFull.phase.id.formatid;
		}

		if(resultFull.phase.converter)
			result.converter = resultFull.phase.converter;
	}
	
	if(testData?.[sampleSubFilePath]?.inputMeta)
		delete testData[sampleSubFilePath].inputMeta;
	
	if(argv.record)
	{
		testData[sampleSubFilePath] = result;
		return pass("r");
	}

	if(!Object.hasOwn(testData, sampleSubFilePath))
		return fail(`No test data for this file: ${xu.inspect(result).squeeze()}`);

	const prevData = testData[sampleSubFilePath];
	if(prevData.processed!==result.processed)
		return fail(`Expected processed to be ${fg.orange(prevData.processed)} but got ${fg.orange(result.processed)}`);

	// TODO check meta differences

	const diskFamily = sampleSubFilePath.split("/")[0];
	if(result.family && result.family!==diskFamily)
		return fail`Disk family ${fg.orange(diskFamily)} does not match processed family ${result.family}`;

	const diskFormatid = sampleSubFilePath.split("/")[1];
	if(result.formatid && result.formatid!==diskFormatid)
		return fail`Disk formatid ${fg.orange(diskFormatid)} does not match processed formatid ${result.formatid}`;

	if(prevData.files && !result.files)
		return fail(`Expected to have ${fg.yellow(Object.keys(prevData.files).length)} files but found ${fg.yellow(0)} instead`);

	if(!prevData.files && result.files)
		return fail(`Expected to have ${fg.yellow(0)} files but found ${fg.yellow(Object.keys(result.files).length)} instead`);
	
	const diffFiles = diffUtil.diff(Object.keys(prevData.files).sortMulti(v => v), Object.keys(result.files).sortMulti(v => v));
	if(diffFiles?.length)
		return fail(`Created files are different: ${fg.orange(diffFiles.join(" "))}`);

	for(const [name, {size, sum, ts}] of Object.entries(result.files))
	{
		const prevFile = prevData.files[name];
		const sizeDiffPercent = 100*(1-((prevFile.size-Math.abs(size-prevFile.size))/prevFile.size));

		// TODO handle sizes that vary just a little bit in output from time to time
		if(sizeDiffPercent!==0)
			return fail`Created file ${fg.peach(name)} differs in size. Expected ${fg.yellow(prevFile.size)} but got ${fg.yellow(size)}`;

		const tsDate = new Date(ts);
		const prevDate = new Date(prevFile.ts || Date.now());
		if(tsDate.getFullYear()<2020 && prevDate.getFullYear()>=2020)
			return fail(`Created file ${fg.peach(name)} ts was not expected to be old, but got old ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}`);

		if(prevDate.getFullYear()<2020 && ts!==prevFile.ts)
			return fail(`Created file ${fg.peach(name)} ts was expected to be ${fg.orange(dateFormat(prevDate, "yyyy-MM-dd"))} but got ${fg.orange(dateFormat(tsDate, "yyyy-MM-dd"))}`);

		if(prevFile.sum!==sum)
			return fail(`Created file ${fg.peach(name)} SHA1 sum differs!`);
	}

	if(prevData.converter && !result.converter)
		return fail(`Expected converter ${fg.orange(prevData.converter)} but did not get one`);

	if(!prevData.converter && result.converter)
		return fail(`Expected no converter but instead got ${fg.orange(result.converter)}`);

	return pass(".");
}

await sampleFilePaths.shuffle().parallelMap(testSample, navigator.hardwareConcurrency);

if(argv.record)
	await fileUtil.writeFile(DATA_FILE_PATH, JSON.stringify(testData));

xu.log`\n\nElapsed time: ${((performance.now()-startTime)/xu.SECOND).secondsAsHumanReadable()}`;
