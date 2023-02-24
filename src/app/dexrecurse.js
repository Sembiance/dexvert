import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {XWorkerPool} from "XWorkerPool";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexvert",
	version : "1.0.0",
	desc    : "Processes <inputFilePath> converting or extracting files RECURSIVELY into <outputDirPath>",
	opts    :
	{
		logLevel    : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"},
		json        : {desc : "If set, will output results as JSON"},
		programFlag : {desc : "One or more program:flagName:flagValue values. If set, the given flagName and flagValue will be used for program", hasValue : true, multiple : true},
		suffix      : {desc : "What suffix to use for output directories. This is important to avoid clobbering other output files.", defaultValue : "§"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The path to the file to convert", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const LOG_EVERY_MS = xu.SECOND*10;
const xlog = new XLog(argv.logLevel);
const NUM_WORKERS = Math.floor(navigator.hardwareConcurrency*0.75);

const programFlag = {};
if(argv.programFlag)
{
	for(const flagRaw of Array.force(argv.programFlag))
	{
		const [programid, flagKey, flagValue] = flagRaw.split(":");

		if(!Object.hasOwn(programFlag, programid))
			programFlag[programid] = {};
		programFlag[programid][flagKey] = (flagValue===undefined ? true : flagValue);
	}
}

let pool=null;
const startedAt=performance.now();
let lastLogTime=performance.now();
let finishedSinceLast=0;
let addedSinceLast=0;
let filesProcessed=0;
async function workercb(workerid, r)	// eslint-disable-line require-await
{
	finishedSinceLast++;
	filesProcessed++;

	if(r.err)
		return xlog.error`${r.inputFilePath} error: ${r.err}`;

	addedSinceLast+=r.createdFiles.length;

	pool.process(r.createdFiles.map(f =>
	{
		const o = {inputFilePath : f.absolute, outDirPath : `${f.absolute}${argv.suffix}`};
		if(argv.json)
			o.jsonFilePath = `${f.absolute}${argv.suffix}.json`;
		if(r.fileMeta?.[f.rel])
			o.fileMeta = r.fileMeta[f.rel];
		return o;
	}));

	const msSinceLast = (performance.now()-lastLogTime);
	if(msSinceLast>LOG_EVERY_MS)
	{
		lastLogTime = performance.now();
		const status = [
			xu.colon("Files"),
			`${fg.chartreuse(pool.busyCount.toString().padStart(NUM_WORKERS.toString().length, " "))} active `,
			`${fg.yellow(pool.queue.length.toLocaleString().padStart(9, " "))} in queue `,
			`${fg.yellowDim(addedSinceLast.toLocaleString().padStart(6, " "))} new `,
			`${fg.orange(filesProcessed.toLocaleString().padStart(9, " "))} done `,
			`${xu.paren(`${fg.deepSkyblue((finishedSinceLast/(msSinceLast/xu.SECOND)).toFixed(2).padStart(6, " "))} per sec`)}`
		];
		xlog.info`${status.join("")}`;
		finishedSinceLast = 0;
		addedSinceLast = 0;
	}
}

let allDone=false;
xlog.info`Starting pool of ${NUM_WORKERS} workers...`;
pool = new XWorkerPool({workercb, emptycb : () => { allDone = true; }, xlog});
await pool.start(path.join(xu.dirname(import.meta), "recurseWorker.js"), {size : NUM_WORKERS});
xlog.info`Starting processing...`;
const o = {inputFilePath : path.resolve(argv.inputFilePath), outDirPath : path.join(path.resolve(argv.outputDirPath), `${path.basename(argv.inputFilePath)}${argv.suffix}`), programFlag};
if(argv.json)
	o.jsonFilePath = path.join(argv.outputDirPath, `${path.basename(argv.inputFilePath)}${argv.suffix}.json`);
pool.process(o);

await xu.waitUntil(() => allDone);
await pool.stop();

xlog.info`\nFinished processing ${fg.deepSkyblue(filesProcessed.toLocaleString())} in ${fg.orange((performance.now()-startedAt).msAsHumanReadable())}`;
