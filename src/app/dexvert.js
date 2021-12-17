import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {dexvert} from "../dexvert.js";
import {DexFile} from "../DexFile.js";
import {Program} from "../Program.js";
import {path} from "std";

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
		dontTransform : {desc : "If a file can't be converted, dexvert will try different transforms (like trimming null bytes) to convert it."},
		programFlag   : {desc : "One or more program:flagName:flagValue values. If set, the given flagName and flagValue will be used for program", hasValue : true, multiple : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The path to the file to convert", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const xlog = xu.xLog(argv.json && !argv.logFile ? "none" : argv.logLevel);

const logLines = [];
if(argv.logFile)
	xlog.logger = v => logLines.push(v);

const dexvertOptions = {};
["asFormat"].forEach(k =>
{
	if(argv[k])
		dexvertOptions[k] = argv[k];
});

async function handleExit(ignored)
{
	if(argv.logFile)
		await Deno.writeTextFile(argv.logFile, `${logLines.join("\n").decolor()}\n`);
	
	Deno.exit(0);
}

let dexState = null;
async function handleDexState(lastTry)
{
	if(!dexState)
	{
		// if no dex state and our last try, just exit
		if(lastTry)
			await handleExit(xlog.warn`No processed result.`);

		return false;
	}

	// send output if we are processed or it's our last try
	const sendOutput = dexState.processed || lastTry;
	if(sendOutput)
	{
		if(argv.jsonFile)
			await Deno.writeTextFile(argv.jsonFile, JSON.stringify(dexState.serialize()));

		if(argv.json)
			console.log(JSON.stringify(dexState.serialize()));
		
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
	}

	// otherwise we were not processed and it's not our last try, so return false and it will try a transform
	return false;
}

const inputFile = await DexFile.create(argv.inputFilePath);
dexState = await dexvert(inputFile, await DexFile.create(argv.outputDirPath), {xlog, ...dexvertOptions});
await handleDexState(argv.dontTransform);

// now we try trimming all trailing 0x00 and 0x1A bytes from files, as these often appear for text files
// then it tries the same trimming but also trimming newlines (sample/text/c/EVAL2.c)
// we used to also do stripGarbage here, which would remove ALL 0x00 bytes from the file and try, but it too often would result in a 'text' match and just wasn't very useful
const TRANSFORM_TYPES = ["trimGarbage", ["trimGarbage", "--newlines"]];	// , "stripGarbage"
for(const [i, transformTypeRaw] of Object.entries(TRANSFORM_TYPES))
{
	const transformDirPath = await fileUtil.genTempPath();
	await Deno.mkdir(transformDirPath);
	const transformFilePath = path.join(transformDirPath, inputFile.base);
	const transformType = Array.isArray(transformTypeRaw) ? transformTypeRaw[0] : transformTypeRaw;
	await runUtil.run(Program.binPath(`${transformType}/${transformType}`), [...(Array.isArray(transformTypeRaw) ? transformTypeRaw.slice(1) : []), inputFile.absolute, transformFilePath]);
	if(!(await fileUtil.exists(transformFilePath)))
	{
		xlog.debug`No transform result for ${Array.force(transformTypeRaw).join(" ")}`;
		await fileUtil.unlink(transformDirPath, {recursive : true});
		continue;
	}
	
	xlog.debug`Attempting dexvert with transform ${Array.force(transformTypeRaw).join(" ")}`;
	const transformedInputFile = await DexFile.create(transformFilePath);
	transformedInputFile.transformed = Array.force(transformTypeRaw).join(" ");
	const transformedDexState = await dexvert(transformedInputFile, await DexFile.create(argv.outputDirPath), {xlog : (xlog.atLeast("debug") ? xlog : xlog.clone("error")), ...dexvertOptions});
	await fileUtil.unlink(transformDirPath, {recursive : true});
	if(transformedDexState.processed)
	{
		dexState = transformedDexState;
		await handleDexState((+i)===(TRANSFORM_TYPES.length-1));
	}
}

// if we got this far, then neither transform produced a file, so we just fall back on our last dexState
await handleDexState(true);
