import {xu, fg} from "xu";
import {XLog} from "xlog";
import {path} from "std";
import {cmdUtil, fileUtil} from "xutil";
import {DEXRPC_HOST, DEXRPC_PORT} from "../server/dexrpc.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexvert",
	version : "1.0.0",
	desc    : "Processes <inputFilePath> converting or extracting files into <outputDirPath>",
	opts    :
	{
		logLevel      : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"},
		logFile       : {desc : "Instead of outputing to stdout, log to a file", hasValue : true},
		asFormat      : {desc : "Convert the format as [family/formatid]. Don't identify the file", hasValue : true},
		json          : {desc : "If set, will output results as JSON"},
		jsonFile      : {desc : "If set, will output results as JSON to the given filePath", hasValue : true},
		programFlag   : {desc : "One or more program:flagName:flagValue values. If set, the given flagName and flagValue will be used for program", hasValue : true, multiple : true},
		forbidProgram : {desc : "A programid not to run. Used internally to prevent infinite recursions", hasValue : true, multiple : true},
		skipVerify    : {desc : "Set to true to skip verifications of output files"},
		fileMeta      : {desc : "JSON representing extra meta info about this file. For example, a previous run of uniso[hfs] will output additional metadata about the files.", hasValue : true},
		direct        : {desc : "Skip going through the dex RPC server and directly load dexvert (still requires dexserver to be running, but allows debugging of src/dexvert.js"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The path to the file to convert", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const xlogOptions = {};
if(argv.logFile)
	xlogOptions.logFilePath = argv.logFile;
const xlog = new XLog(argv.json && !argv.logFile ? "none" : argv.logLevel, xlogOptions);

const dexvertOptions = {};
if(argv.programFlag)
{
	dexvertOptions.programFlag = {};
	for(const flagRaw of Array.force(argv.programFlag))
	{
		const [programid, flagKey, flagValue] = flagRaw.split(":");

		if(!Object.hasOwn(dexvertOptions.programFlag, programid))
			dexvertOptions.programFlag[programid] = {};
		dexvertOptions.programFlag[programid][flagKey] = (flagValue===undefined ? true : flagValue);
	}
}

["asFormat", "forbidProgram", "skipVerify"].forEach(k =>
{
	if(argv[k])
		dexvertOptions[k] = argv[k];
});

async function handleExit(ignored)
{
	await xlog.flush();
	Deno.exit(0);
}

if(argv.direct)
{
	const {init : initPrograms} = await import(path.join(import.meta.dirname, "../program/programs.js"));
	const {init : initFormats} = await import(path.join(import.meta.dirname, "../format/formats.js"));

	await initPrograms();
	await initFormats();

	const {DexFile} = await import(path.join(import.meta.dirname, "../DexFile.js"));
	const {dexvert} = await import(path.join(import.meta.dirname, "../dexvert.js"));

	const dexState = await dexvert(await DexFile.create(argv.inputFilePath), await DexFile.create(argv.outputDirPath), {xlog, ...dexvertOptions});
	console.log(dexState.pretty());

	await handleExit();
}

const rpcData = {op : "dexvert", inputFilePath : path.resolve(argv.inputFilePath), outputDirPath : path.resolve(argv.outputDirPath), logLevel : argv.logLevel, fileMeta : xu.parseJSON(argv.fileMeta), dexvertOptions};
const {r, logLines} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(rpcData)}))?.json()), {});
if(!r && !logLines)
	Deno.exit(console.error(`Failed to contact dexserver at ${fg.cyan(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`)} is it running?`));

if(!argv.json && logLines.length)
	console.log(`${logLines.join("\n")}\n`);

if(!r)
	await handleExit(xlog.warn`No processed result.`);

if(argv.jsonFile)
	await fileUtil.writeTextFile(argv.jsonFile, JSON.stringify(r.json));

if(argv.json)
	console.log(JSON.stringify(r.json));

if(xlog.atLeast("fatal"))
{
	if(argv.logFile)
	{
		xlog.info`${r.pretty}`;
		if(logLines.length)
			xlog.info`${logLines.join("\n")}`;
	}
	else if(!argv.json)
	{
		xlog.debug`Outputting prettyfied state to console...`;
		console.log(`${r.pretty}`);
	}
}

await handleExit();
