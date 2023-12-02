import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, runUtil, printUtil} from "xutil";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexdeep",
	version : "1.0.0",
	desc    : "Processes <inputFilePath> trying dexvert on every single byte offset and saving results in <outputDirPath>",
	opts    :
	{
		family : {desc : "Restrict results only to this family (comma delimited list allowed)", hasValue : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The path to the file to process", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const xlog = new XLog("info");

await fileUtil.unlink(path.resolve(argv.outputDirPath), {recursive : true});
await Deno.mkdir(path.resolve(argv.outputDirPath));

const {size : FILE_SIZE} = await Deno.stat(argv.inputFilePath);

let completed = 0;
let completedMark=0;
const atOnce = navigator.hardwareConcurrency;
const partSize = Math.floor(FILE_SIZE/atOnce);
xlog.info`Processing ${FILE_SIZE} bytes, doing ${atOnce} ops at once.`;

[].pushSequence(0, atOnce).parallelMap(async partid =>
{
	for(let offset=(partid*partSize);offset<Math.min(FILE_SIZE-1, ((partid+1)*partSize));offset++)
	{
		const tmpInputFilePath = await fileUtil.genTempPath(undefined, undefined);
		await runUtil.run("dd", ["bs=1", `skip=${offset}`, `if=${argv.inputFilePath}`, `of=${tmpInputFilePath}`]);

		const outputDirPath = path.join(path.resolve(argv.outputDirPath), offset.toString());
		await Deno.mkdir(outputDirPath, {recursive : true});

		const {stdout} = await runUtil.run("deno", runUtil.denoArgs(path.join(xu.dirname(import.meta), "dexvert.js"), "--logLevel=none", "--json", tmpInputFilePath, outputDirPath), {env : runUtil.denoEnv()});
		await fileUtil.unlink(tmpInputFilePath);

		const result = xu.parseJSON(stdout, {});
		if(!result.processed || !result?.phase?.family || result.phase.family==="text")
		{
			printUtil.stdoutWrite(".");
			completed++;
			const newMark = Math.floor((completed/FILE_SIZE)*10);
			if(newMark>completedMark)
			{
				completedMark = newMark;
				printUtil.stdoutWrite(fg.yellow(`${completedMark}0%`));
			}
			await fileUtil.unlink(outputDirPath, {recursive : true});
		}
		else
		{
			await Deno.rename(outputDirPath, path.join(path.dirname(outputDirPath), `${result.phase.family}-${result.phase.format}-${offset}`));
			xlog.info`Offset ${offset} matched ${result.phase.family}/${result.phase.format}`;
		}
	}
}, atOnce);
