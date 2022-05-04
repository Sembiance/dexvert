/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil} from "xutil";
import {path, delay, base64Encode} from "std";
//import {formats, reload as reloadFormats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {getDetections} from "../src/Detection.js";
//import {identify} from "../src/identify.js";

const xlog = new XLog("error");

const SAMPLE_DIR_PATH_SRC = path.join(xu.dirname(import.meta), "..", "test", "sample");
const SAMPLE_DIR_PATH = "/mnt/ram/dexvert/sample";

console.log("Rsyncing sample files to RAM...");
await runUtil.run("rsync", ["--delete", "-savL", path.join(SAMPLE_DIR_PATH_SRC, "/"), path.join(SAMPLE_DIR_PATH, "/")]);

const SUPPORTING_DIR_PATHS =
[
	"music/Instruments"
];

const IGNORED_FMTIDS =
[
	111,	// ASCII
	208,	// Binary
	1555	// text
];

const IGNORED_XFMTIDS =
[
	111,	// OLE2
	157,	// IFF
	195		// Generic Markup
];

const sampleFilePaths = await fileUtil.tree(SAMPLE_DIR_PATH, {nodir : true, depth : 3});
sampleFilePaths.filterInPlace(sampleFilePath => !SUPPORTING_DIR_PATHS.some(v => path.relative(SAMPLE_DIR_PATH, sampleFilePath).startsWith(v)));

const newMagics = {};

const startedAt = performance.now();
let completed=0;
let completedMark=0;
async function idSample(sampleFilePath)
{
	const sampleSubFilePath = path.relative(SAMPLE_DIR_PATH, sampleFilePath);
	const diskFamily = sampleSubFilePath.split("/")[0];
	const diskFormat = sampleSubFilePath.split("/")[1];
	const diskFormatid = `${diskFamily}/${diskFormat}`;

	let foundNewMagic = false;
	//const ids = await identify(sampleFilePath, {logLevel : "error"});
	//const {stdout : idsRaw} = await runUtil.run("deno", runUtil.denoArgs(path.join(xu.dirname(import.meta), "..", "src", "app", "dexid.js"), "--json", sampleFilePath), runUtil.denoRunOpts());
	//const ids = xu.parseJSON(idsRaw);
	//if(!ids)
	//	return;
	
	const ids = await getDetections(await DexFile.create(sampleFilePath), {xlog, detectors : ["siegfried"]});
	for(const id of ids)
	{
		if(id.from!=="siegfried" || IGNORED_FMTIDS.some(IGNORED_FMTID => id.value.startsWith(`fmt/${IGNORED_FMTID}`)) || IGNORED_XFMTIDS.some(IGNORED_XFMTID => id.value.startsWith(`x-fmt/${IGNORED_XFMTID}`)))
			continue;

		if(!newMagics[diskFormatid])
			newMagics[diskFormatid] = new Set();
		
		if(newMagics[diskFormatid].has(id.value))
			continue;

		foundNewMagic = true;
		newMagics[diskFormatid].add(id.value);

		//if(Object.values(newMagics).length>10)
		//	printResults();
	}

	xu.stdoutWrite(foundNewMagic ? fg.white("·") : fg.fogGray("."));
	completed++;

	const newMark = Math.floor((completed/sampleFilePaths.length)*10);
	if(newMark>completedMark)
	{
		completedMark = newMark;
		xu.stdoutWrite(fg.yellow(`${completedMark}0%`));
	}
}

await sampleFilePaths.parallelMap(idSample, navigator.hardwareConcurrency*1.25);
printResults();

function printResults()
{
	console.log("");

	const forHumans = Object.entries(newMagics).map(([k, v]) =>
	{
		const magics = [];
		const magicNames = [];
		for(const value of Array.from(v.values()).sortMulti([m => +m.split(" ")[0].split("/")[1]]))
		{
			const [magic, ...magicName] = value.split(" ");
			magics.push(magic);
			if(magicName?.length)
				magicNames.push(magicName.join(" "));
		}
		return {formatid : k, magics : `, ${magics.map(val => `"${val}"`).join(", ")}`, magicNames : `[${magicNames.join("] [")}]`};
	});

	console.log(printUtil.columnizeObjects(forHumans));
	console.log(`\nTook: ${((performance.now()-startedAt)/xu.SECOND).toFixed(2)} seconds`);
	Deno.exit(0);
}
