import {xu} from "xu";
import {cmdUtil} from "xutil";
import {dexvert} from "../dexvert.js";
import {DexFile} from "../DexFile.js";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <inputFilePath> converting or extracting files into <outputDirPath>",
	opts    :
	{
		logLevel      : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"},
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

const xlog = xu.xLog(argv.json ? "none" : argv.logLevel);

const debugLog = [];
if(argv.logLevel==="debug")
{
	xlog.level = "debug";
	xlog.logger = v => debugLog.push(v);
}

const dexvertOptions = {xlog};
["asFormat"].forEach(k =>
{
	if(argv[k])
		dexvertOptions[k] = argv[k];
});

async function handleDexState(dexState, lastTry)
{
	if(!dexState)
	{
		// if no dex state and our last try, just exit
		if(lastTry)
		{
			xlog.warn`No processed result.`;
			Deno.exit(0);
		}

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
		else if(xlog.atLeast("fatal"))
			console.log(`${dexState.pretty()}`);
		
		// if we are not processed, then by default this is our lastTry so output that we have no result
		if(!dexState.processed)
		{
			xlog.warn`No processed result.`;

			if(argv.logLevel==="debug")
				console.log(`Processing failed: ${debugLog.join("\n")}`);
		}

		Deno.exit(0);
	}

	// otherwise we were not processed and it's not our last try, so return false and it will try a transform
	return false;
}

await handleDexState(await dexvert(await DexFile.create(argv.inputFilePath), await DexFile.create(argv.outputDirPath), dexvertOptions), true);	// TODO remove the last true here and put on the last transform once those are added back

if(argv.dontTransform)
{
	xlog.warn`No processed result, but option ${"dontTransform"} was specified so NOT trying any transforms.`;
	Deno.exit(0);
}

// TODO do the two transforms now BELOW
// TRANSFORMED --- ROB DENO NOTE!
//     As soon as I do a successful transform process, make sure it proudly shows up in the DexState output
//     Then run a full test suite, see if anything new mis-identifies, those formats it mis-converts as might not be safe to operate on transformed formats. Already have support for that, just need to set 'transformUnsafe = true;' to the format
// Lastly, consider adding to Program.js to never operate on files marked .transformed if the program is also marked .unsafe (this would be a new addition)
// TODO do the two transforms now ABOVE

/*
const argv = cmdUtil.cmdInit(cmdData);
const verbose = +(argv.verbose || 0);

tiptoe(
	function runProcess()
	{
		const processOptions = {verbose, programFlags : {}};
		["useTmpOutputDir", "brute", "asFormat", "keepGoing", "alwaysBrute", "brutePrograms", "dontTransform"].forEach(k =>
		{
			if(argv.hasOwnProperty(k))
				processOptions[k] = ["brute"].includes(k) ? argv[k].split(",") : argv[k];
		});
		
		Array.force(argv.programFlag || []).forEach(flag =>
		{
			const flagProps = (flag.match(/(?<p>[^:]+):(?<k>[^:]+):(?<v>.+)/) || {groups : {}}).groups;
			if(!processOptions.programFlags[flagProps.p])
				processOptions.programFlags[flagProps.p] = {};
			processOptions.programFlags[flagProps.p][flagProps.k] = flagProps.v;
		});

		dexvert.process(argv.inputFilePath, argv.outputDirPath, processOptions, this);
	},
	function printResults(state)
	{
		if(argv.outputStateToFile)
			return fs.writeFile(argv.outputStateToFile, JSON.stringify(state), XU.UTF8, this);

		if(argv.outputState)
			console.log(JSON.stringify(state));
		else if(state.verbose>=2)
			console.log(util.inspect(state, {colors : true, depth : Infinity}));

		this();
	},
	XU.FINISH
);
*/
