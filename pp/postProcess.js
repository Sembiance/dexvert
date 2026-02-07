import {xu} from "xu";
import {cmdUtil, fileUtil, printUtil, webUtil} from "xutil";
import {XLog} from "xlog";
import {path} from "std";
import {C, ALLOWED_PP_ERRORS} from "./ppUtil.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "postProcess",
	version : "1.0.0",
	desc    : "Takes the dexrecurse results, runs the files through various AI models, generates thumbnails, and packs everything into sparkey DBs",
	opts    :
	{
		itemMetaURL : {desc : "A URL to fetch itemMeta data from", hasValue : true, required : true},
		headless    : {desc : "Run headless, no GUI"},
		logLevel    : {desc : "Set log level (error, warn, info, debug)", hasValue : true, defaultValue : "info"}
	},
	args :
	[
		{argid : "itemDirPath", desc : "The path to the item dexrecurse outputs including file & meta subdirs", required : true}
	]});

const xlog = new XLog(argv.headless ? "error" : argv.logLevel);

const phases =
[
	{ num :  1, description : "file & directory renaming" },
	{ num :  2, description : "properties setting" },
	{ num :  3, description : "content info & thumb generation" },
	{ num :  4, description : "extraction of textContent" },
	{ num :  5, description : "image classification & vectorization" },
	{ num :  6, description : "audio & video transcription" },
	{ num :  7, description : "audio vectorization" },
	{ num :  8, description : "search engine index preperation" },
	{ num :  9, description : "cleanup webData" },
	{ num : 10, description : "pack into sparkey DBs" }
];

const item = await xu.fetch(argv.itemMetaURL, {asJSON : true});
const itemDirPath = path.resolve(argv.itemDirPath);

const itemWebDirPath = path.join(itemDirPath, "web");
const itemThumbDirPath = path.join(itemDirPath, "thumb");
const itemClassifyDirPath = path.join(itemDirPath, "classify");
const itemClassifyTmpDirPath = path.join(itemClassifyDirPath, "tmp");
const itemFileDirPath = path.join(itemDirPath, "file");
const itemMetaDirPath = path.join(itemDirPath, "meta");

const reportFilePath = path.join(itemDirPath, "report.json");
let report = xu.parseJSON(await fileUtil.readTextFile(reportFilePath));
report.postProcess = {item};
await fileUtil.writeTextFile(reportFilePath, JSON.stringify(report));

const phaseArgs = {item, itemDirPath, itemFileDirPath, itemThumbDirPath, itemMetaDirPath, itemWebDirPath, itemClassifyDirPath, itemClassifyTmpDirPath, reportFilePath, xlog};

const errors = [];

class TaskRunner
{
	phase = {num : 0, description : "idle"};

	constructor()
	{
		this.startedAt = performance.now();
	}

	async phaseStart(phase)
	{
		delete this.max;
		delete this.bar;
		this.count = 0;

		this.phaseStartedAt = performance.now();

		this.phase = phase;
		if(!argv.headless)
			console.log(printUtil.majorHeader(`phase ${this.phase.num}: ${this.phase.description}`, {prefix : "\n"}));

		const {default : phaseFunc} = await import(path.join(import.meta.dirname, "phase", `phase${phase.num}.js`));
		await phaseFunc(phaseArgs);
	}

	startProgress(max, msg)
	{
		this.msg = msg;

		if(this.bar)
		{
			this.bar.finish();
			delete this.bar;
		}

		if(msg && !argv.headless)
			xlog.info`\n${msg}`;

		this.max = max;
		this.count = 0;

		if(!argv.headless && !this.bar && max!==undefined)
			this.bar = printUtil.progress({max, dontAutoFinish : true});
	}

	addError(errorMsg, critical)
	{
		if(!critical && ALLOWED_PP_ERRORS.some(m => (typeof m==="string" ? errorMsg.includes(m) : m.test(errorMsg))))
			return;

		if(!argv.headless)
			xlog.error`${critical ? "CRITICAL ERROR: " : ""}${errorMsg}`;
		if(critical)
			console.error`CRITICAL ERROR: ${errorMsg}`;
		errors.push(`Phase ${this.phase.num} ${critical ? "CRITICAL " : ""}error: ${errorMsg}`);
	}

	setMax(max)
	{
		this.max = max;

		if(!argv.headless && this.bar)
			this.bar.setMax(max);
	}

	incrementBy(amount)
	{
		this.count+=amount;
		if(this.bar)
			this.bar.incrementBy(amount);
	}

	increment(msg)
	{
		this.count++;
		if(msg)
			this.msg = msg;

		if(this.bar)
		{
			this.bar.increment();
			if(msg)
				this.bar.setStatus(msg);
		}
	}

	phaseComplete()
	{
		this.phaseFinishedAt = performance.now();
		this.phaseDuration = this.phaseFinishedAt-this.phaseStartedAt;

		if(this.bar)
		{
			this.bar.finish();
			delete this.bar;
		}

		if(!argv.headless)
			xlog.info`Phase Duration: ${this.phaseDuration.msAsHumanReadable()}`;
	}

	getDuration()
	{
		return performance.now()-this.startedAt;
	}

	getStatus()
	{
		return {duration : this.getDuration(), phaseNum : this.phase.num, phaseDescription : this.phase.description, msg : this.msg, max : this.max, count : this.count};
	}
}

const taskRunner = new TaskRunner();
phaseArgs.taskRunner = taskRunner;

let running = true;

const routes = new Map();
routes.set("/status", () =>
{
	const r = taskRunner.getStatus();
	if(!running)
		r.complete = true;
	return Response.json(r);
});
const webServer = webUtil.serve({hostname : C.POST_PROCESS_HOST, port : C.POST_PROCESS_PORT}, await webUtil.route(routes), {xlog});

taskRunner.startProgress(2, `Post Processing ${itemDirPath} as itemid ${item.itemid}...`);

await Deno.mkdir(itemWebDirPath, {recursive : true});
await Deno.mkdir(itemThumbDirPath, {recursive : true});
await Deno.mkdir(itemClassifyTmpDirPath, {recursive : true});

for(const phase of phases)
	await taskRunner.phaseStart(phase);

// phases are done, finalize our stats
report = xu.parseJSON(await fileUtil.readTextFile(reportFilePath), {});
report.postProcess.duration = taskRunner.getDuration();
report.postProcess.errors = errors;
await fileUtil.writeTextFile(reportFilePath, JSON.stringify(report));

if(errors.length)
{
	xlog.warn`\nGot ${errors.length} errors during post processing:`;
	for(const v of errors)
		xlog.warn`${v}`;
}

await fileUtil.unlink(itemWebDirPath, {recursive : true});
await fileUtil.unlink(itemThumbDirPath, {recursive : true});
await fileUtil.unlink(itemClassifyDirPath, {recursive : true});
await fileUtil.unlink(itemFileDirPath, {recursive : true});
await fileUtil.unlink(itemMetaDirPath, {recursive : true});

running = false;
await webServer.stop();

xlog.info`\nDone! Took ${report.postProcess.duration.msAsHumanReadable()}`;
