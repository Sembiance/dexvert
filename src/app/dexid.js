import {xu, fg} from "xu";
import {cmdUtil, printUtil} from "xutil";
import {identify} from "../identify.js";
import {DexFile} from "../DexFile.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexid",
	version : "1.0.0",
	desc    : "Identifies one or more files",
	opts    :
	{
		verbose  : {desc : "Show additional info when identifying. Levels 0 to 5. Default: 0", defaultValue : 0},
		json     : {desc : "Output JSON"},
		jsonFile : {desc : "If set, will output the result JSON to the given filePath", hasValue : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "One or more file paths to identify", required : true, multiple : true}
	]});

xu.verbose = argv.json ? 0 : argv.verbose;

const inputFilePaths = Array.force(argv.inputFilePath);
for(const inputFilePath of inputFilePaths)
{
	const rows = await identify(await DexFile.create(inputFilePath));

	if(argv.jsonFile)
		await Deno.writeTextFile(argv.jsonFile, JSON.stringify(rows));

	if(argv.json)
	{
		console.log(JSON.stringify(rows));
		Deno.exit(0);
	}

	if(inputFilePaths)
		xu.log`${xu.colon(fg.peach("File"))} ${inputFilePath}`;
	const maxes =
	{
		matchType : rows.map(({matchType}) => (matchType || "").length).max(),
		family    : rows.map(({family}) => (family || "").length).max()
	};
	const printRows = rows.map(({from, family, confidence, magic, extensions, matchType, formatid, unsupported}) => ({
		from : from==="dexvert" ? fg.green(from) : from,
		confidence,
		format : `${from!=="dexvert" ? magic.innerTruncate(75) : magic}${unsupported ? fg.deepSkyblue(" unsupported") : ""}`,
		extensions,
		dexvert : `${from!=="dexvert" ? "" : `${fg.peach(matchType.padStart(maxes.matchType))} ${fg.yellow(family.padStart(maxes.family))}${fg.cyan("/")}${fg.yellowDim(formatid)}`}`}));
	console.log(printUtil.columnizeObjects(printRows, {
		colNameMap : {confidence : "%"},
		color      : {confidence : "white"}}));
}
