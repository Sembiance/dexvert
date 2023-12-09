import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, runUtil, printUtil} from "xutil";
import {path} from "std";
import {DEXRPC_HOST, DEXRPC_PORT} from "../server/dexrpc.js";

const MAX_DURATION = xu.HOUR;

const argv = cmdUtil.cmdInit({
	cmdid   : "dexvert",
	version : "1.0.0",
	desc    : "Processes <inputFilePath> converting or extracting files RECURSIVELY into <outputDirPath>",
	opts    :
	{
		programFlag : {desc : "One or more program:flagName:flagValue values. If set, the given flagName and flagValue will be used for program", hasValue : true, multiple : true},
		suffix      : {desc : "What suffix to use for output directories. This is important to avoid clobbering other output files.", defaultValue : "§"}
	},
	args :
	[
		{argid : "inputPath", desc : "A single file or directory of files to recurse", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const xlog = new XLog();

if(!(await fileUtil.exists(argv.outputDirPath)))
	Deno.exit(xlog.error`Output directory ${argv.outputDirPath} does not exist!`);

if((await fileUtil.tree(argv.outputDirPath)).length>0)
	Deno.exit(xlog.error`Output directory ${argv.outputDirPath} is not empty!`);

const WORKER_COUNT = +(await xu.fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/workerCount`));

const fileDirPath = path.join(argv.outputDirPath, "file");
await Deno.mkdir(fileDirPath);

const metaDirPath = path.join(argv.outputDirPath, "meta");
await Deno.mkdir(metaDirPath);

if((await Deno.stat(argv.inputPath)).isFile)	// eslint-disable-line unicorn/prefer-ternary
	await runUtil.run("rsync", runUtil.rsyncArgs(argv.inputPath, path.join(fileDirPath, path.basename(argv.inputPath)), {fast : true}));
else
	await runUtil.run("rsync", runUtil.rsyncArgs(path.join(argv.inputPath, "/"), path.join(fileDirPath, "/"), {fast : true}));

const taskQueue = await fileUtil.tree(fileDirPath, {nodir : true, relative : true});
const taskActive = new Set();
const bar = printUtil.progress({max : taskQueue.length});

async function processNextQueue()
{
	const task = {relFilePath : taskQueue.shift(), startedAt : performance.now()};
	taskActive.add(task);

	task.relDirPath = path.dirname(task.relFilePath)==="." ? "" : path.dirname(task.relFilePath);
	task.fileOutDirPath = path.join(fileDirPath, task.relDirPath, `${path.basename(task.relFilePath)}${argv.suffix}`);
	await Deno.mkdir(task.fileOutDirPath, {recursive : true});

	task.metaFilePath = path.join(metaDirPath, task.relDirPath, `${path.basename(task.relFilePath)}.json`);
	task.logFilePath = path.join(metaDirPath, task.relDirPath, `${path.basename(task.relFilePath)}.txt`);
	await Deno.mkdir(path.dirname(task.metaFilePath), {recursive : true});

	try
	{
		const rpcData = {op : "dexvert", inputFilePath : path.join(fileDirPath, task.relFilePath), outputDirPath : task.fileOutDirPath, logLevel : "info", timeout : MAX_DURATION+(xu.SECOND*10)};
		const dexText = await xu.fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {timeout : MAX_DURATION, json : rpcData});
		if(!dexText)
			throw new Error(`No data returned from dexrpc for ${task.relFilePath}`);

		const {r, logLines} = xu.parseJSON(dexText, {});
		if(!r?.json)
			throw new Error(`Invalid JSON response from dexrpc for ${task.relFilePath}:\n${dexText}`);

		const dexData = r.json;

		const meta = {dexData, dexDuration : performance.now()-task.startedAt, task};
		await fileUtil.writeTextFile(task.metaFilePath, JSON.stringify(meta));
		await fileUtil.writeTextFile(task.logFilePath, `${r.pretty}\n${(logLines || []).join("\n")}`);

		if(!dexData?.created?.files?.output?.length)
		{
			await fileUtil.unlink(task.fileOutDirPath);
		}
		else
		{
			for(const file of dexData.created.files.output)
			{
				bar.incrementMax();
				taskQueue.push(path.relative(fileDirPath, file.absolute));
			}
		}
	}
	catch(err)
	{
		await fileUtil.writeTextFile(task.logFilePath, err.toString(), {append : true});
		if(!(await fileUtil.exists(task.metaFilePath)))
			await fileUtil.writeTextFile(task.metaFilePath, JSON.stringify({failed : true, err : err.toString(), stack : err.stack}));
	}

	bar.increment();
	taskActive.delete(task);
}

const startedAt = performance.now();
await xu.waitUntil(async () =>	// eslint-disable-line require-await
{
	if(taskActive.size===0 && taskQueue.length===0)
		return true;

	while(taskQueue.length>0 && taskActive.size<WORKER_COUNT)
		processNextQueue();	// eslint-disable-line no-floating-promise/no-floating-promise

	const slowestTask = Array.from(taskActive).sortMulti([v => v.startedAt])[0];
	bar.setStatus(` A:${taskActive.size.toLocaleString()}  Q:${taskQueue.length.toLocaleString()}  ${(performance.now()-slowestTask.startedAt).msAsHumanReadable({short : true})} ${slowestTask.relFilePath.innerTruncate(30)}`);

	return false;
}, {interval : 100});

xlog.info`\nTotal Duration: ${(performance.now()-startedAt).msAsHumanReadable()}`;

/*
  Create in meta a single  "§.json" which represents the stats for that FOLDER. This is calcualted AFTER everything is all done and contains sub-counts for sub-folders, lists of what is in current folder and everything else needed to rendfer in retromission

  It should also create a <outputDir>/report.html with new magics, new file samples, etc similar to what retroadmin used to do
  For new file samples, get a count of each formatid on disk (in dexvert/test/sample). Never copy more than '3' new samples. Never want more than 10 total of each type. So if existingCount[formatid]<10: needCount = Math.min(3, 10-existingCount[formatid]). b3sum existing files of course and only include 'new ones'. Group the new files ext and pick one from each ext up until we have needCount. If still need more (OR IF WE ONLY HAVE 1 EXTENSION), stick all the files into an array (removing those already gonna copy by ext) and sort the array by file size, then take the largest, smallest and one from middle.
  Group files for that formatid by ex
  Possibly the JSON generated to create report.html, also save that out was <outputDir>/report.json
  Test with CD #3 and some other early items, see how it works.
*/
