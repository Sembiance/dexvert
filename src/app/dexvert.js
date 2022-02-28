import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {dexvert} from "../dexvert.js";
import {DexFile} from "../DexFile.js";

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
		skipVerify    : {desc : "Set to true to skip verifications of output files"}
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
		dexvertOptions.programFlag[programid][flagKey] = (typeof flagValue==="undefined" ? true : flagValue);
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

const inputFile = await DexFile.create(argv.inputFilePath);
const dexState = await dexvert(inputFile, await DexFile.create(argv.outputDirPath), {xlog, ...dexvertOptions});
if(!dexState)
	await handleExit(xlog.warn`No processed result.`);

const serializedState = (argv.jsonFile || argv.json) ? JSON.stringify(dexState.serialize()) : null;

if(argv.jsonFile)
	await Deno.writeTextFile(argv.jsonFile, serializedState);

if(argv.json)
	console.log(serializedState);

if(xlog.atLeast("fatal"))
{
	if(argv.logFile)
		xlog.warn`${dexState.pretty()}`;
	else if(!argv.json)
		console.log(`${dexState.pretty()}`);
}

// if we are not processed, then by default this is our lastTry so output that we have no result
if(!dexState.processed)
	xlog.warn`No processed result.`;

await handleExit();
