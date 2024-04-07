import {xu, fg} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil, cmdUtil, printUtil} from "xutil";
import {path} from "std";
import {identify} from "../src/identify.js";
import {init as initFormats} from "../src/format/formats.js";
import {init as initPrograms} from "../src/program/programs.js";

const xlog = new XLog();
await initPrograms(xlog);
await initFormats(xlog);

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Scans a given file for all possible identifications by offsetting bytes",
	opts    :
	{
		maxOffset : {desc : "Maximum offset to process", hasValue : true, defaultValue : 1000}
	},
	args :
	[
		{argid : "inputFilePath", desc : "Input bad 7z CUR file to parse", required : true}
	]});

const {size : FILE_SIZE} = await Deno.stat(argv.inputFilePath);

let completed = 0;
let completedMark=0;
const atOnce = navigator.hardwareConcurrency;
const partSize = Math.floor(argv.maxOffset/atOnce);
xlog.info`Processing ${FILE_SIZE} bytes, doing ${atOnce} ops at once. Max Offset: ${argv.maxOffset}`;

const ids = {};

await [].pushSequence(0, atOnce).parallelMap(async partid =>
{
	for(let offset=(partid*partSize);offset<Math.min(argv.maxOffset, ((partid+1)*partSize));offset++)
	{
		const tmpInputFilePath = await fileUtil.genTempPath(undefined, path.extname(argv.inputFilePath));
		await runUtil.run("dd", ["bs=1", `skip=${offset}`, `if=${argv.inputFilePath}`, `of=${tmpInputFilePath}`]);

		const {ids : r} = await identify(tmpInputFilePath, {xlog : new XLog("none")});
		for(const id of r)
		{
			if(id.matchType!=="magic")
				continue;
			ids[id.magic] ||= [];
			ids[id.magic].push(offset);
		}

		printUtil.stdoutWrite(".");
		completed++;
		const newMark = Math.floor((completed/FILE_SIZE)*10);
		if(newMark>completedMark)
		{
			completedMark = newMark;
			printUtil.stdoutWrite(fg.yellow(`${completedMark}0%`));
		}
	}
}, atOnce);

console.log(ids);
