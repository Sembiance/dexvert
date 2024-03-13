import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, printUtil, cmdUtil} from "xutil";
import {Program} from "../src/Program.js";
import {FileSet} from "../src/FileSet.js";
import {DETECTOR_PROGRAMS} from "../src/Detection.js";
import {init as initPrograms} from "../src/program/programs.js";
import {formats, init as initFormats} from "../src/format/formats.js";
import {path} from "std";
import {flexMatch} from "../src/identify.js";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test a new detector program and outputs all found non-weak magics that are not already in any formats magic list",
	opts    :
	{
		showWeak : {desc : "If you set this to true, even matches marked 'weak' will show up"},
		unique   : {desc : "Set this to filter out duplicated magic values and only show 1 of each magic string"},
		program  : {desc : "Which program to run (or all)", required : true, hasValue : true, allowed : [...DETECTOR_PROGRAMS, "all"]},
		format   : {desc : "Specify one or more formats. Can specify 'all' or an entire family like 'image' or partials like 'image/a'", required : true, hasValue : true, multiple : true}
	}});

const detectorsToTest = argv.program==="all" ? Array.from(DETECTOR_PROGRAMS) : [argv.program];

await initPrograms(xlog);
await initFormats(xlog);

const ALL_MAGICS = new Set();
for(const format of Object.values(formats))
{
	for(const m of Array.force(format.magic || []))
		ALL_MAGICS.add(m);
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

const formatsToProcess = new Set();
for(const format of Object.values(formats))
{
	if(format.unsupported)
		continue;

	const formatid = `${format.family.familyid}/${format.formatid}`;
	if(argv.format[0]==="all" || argv.format.some(v => formatid.startsWith(v)))
		formatsToProcess.add(formatid);
}

const SAMPLES_DIR_PATH = path.join(import.meta.dirname, "..", "test", "sample");

console.log(printUtil.minorHeader(`${formatsToProcess.size.toLocaleString()} formats - Locating samples`, {prefix : "\n"}));
let bar = printUtil.progress({max : formatsToProcess.size});
const sampleFilePaths = (await Array.from(formatsToProcess).parallelMap(async formatid =>
{
	const r = await fileUtil.tree(path.join(SAMPLES_DIR_PATH, formatid), {nodir : true, depth : 1});
	bar.increment();
	return r;
})).flat();


async function checkDetector(detectorid)
{
	console.log(printUtil.majorHeader(`${detectorid}`, {prefix : "\n"}));
	bar = printUtil.progress({max : sampleFilePaths.length});
	const matches = [];
	await sampleFilePaths.shuffle().parallelMap(async sampleFilePath =>
	{
		const r = await Program.runProgram(detectorid, await FileSet.create(path.dirname(sampleFilePath), "input", sampleFilePath), {xlog : new XLog("error")});
		bar.increment();
		if(!r?.meta?.detections?.length)
			return;

		const detection = r.meta.detections[0];
		if(detection.weak && !argv.showWeak)
			return;

		const magic = detection.value.trim();
		if(isExistingMagic(magic))
			return;

		const [family, format] = path.relative(SAMPLES_DIR_PATH, sampleFilePath).split("/");
		matches.push({formatid : `${family}/${format}`, filename : path.basename(sampleFilePath).innerTruncate(30), magic : magic.innerTruncate(65)});
	}, -1);

	if(argv.unique)
	{
		const uniqueMagics = [];
		matches.filterInPlace(o =>
		{
			if(!uniqueMagics.includes(o.magic))
			{
				uniqueMagics.push(o.magic);
				return true;
			}

			return false;
		});
	}

	console.log(printUtil.columnizeObjects(matches.sortMulti([o => o.formatid.split("/")[0], o => o.formatid.split("/")[1]]), {prefix : "\n\n"}));
}

for(const detectorid of detectorsToTest)
	await checkDetector(detectorid);
