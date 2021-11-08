import {xu} from "xu";
import {cmdUtil} from "xutil";
import {dexvert} from "../dexvert.js";
import {DexFile} from "../DexFile.js";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <inputFilePath> converting or extracting files into <outputDirPath>",
	opts    :
	{
		verbose         : {desc : "Show additional info when processing. Levels 0 to 5. Default: 0", defaultValue : 0},
		asFormat        : {desc : "Convert the format as [family/formatid]. Don't identify the file", hasValue : true},
		json            : {desc : "If set, will output results as JSON"},
		jsonFile        : {desc : "If set, will output results as JSON to the given filePath", hasValue : true},
		dontTransform   : {desc : "If a file can't be converted, dexvert will try different transforms (like trimming null bytes) to convert it."},
		programFlag     : {desc : "One or more program:flagName:flagValue values. If set, the given flagName and flagValue will be used for program", hasValue : true, multiple : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The path to the file to convert", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const dexvertOptions = {};
["verbose", "asFormat"].forEach(k =>
{
	if(argv[k])
		dexvertOptions[k] = argv[k];
});

const r = await dexvert(await DexFile.create(argv.inputFilePath), await DexFile.create(argv.outputDirPath), dexvertOptions);
if(r)
	console.log(`\n${r.pretty()}`);
// TODO if no results, transform.   transform code should move into bin/*/

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
