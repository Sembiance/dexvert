import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, printUtil, runUtil} from "xutil";
import {path} from "std";
import {DexFile} from "../DexFile.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexid",
	version : "1.0.0",
	desc    : "Identifies one or more files",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "warn"},
		json     : {desc : "Output JSON"},
		jsonFile : {desc : "If set, will output the result JSON to the given filePath", hasValue : true},
		rebuild  : {desc : "Rebuild formats and programs first"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "One or more file paths to identify", required : true, multiple : true}
	]});

const xlog = new XLog(argv.logLevel);

if(argv.rebuild)
	await runUtil.run("./build", ["programs", "formats"], {cwd : path.join(xu.dirname(import.meta), "..", "..", "build"), liveOutput : true});

const {identify} = await import(`../identify.js?v=${xu.randStr()}`);

const inputFilePaths = Array.force(argv.inputFilePath);
for(const inputFilePath of inputFilePaths)
{
	const rows = await identify(await DexFile.create(inputFilePath), {xlog});

	if(argv.jsonFile)
		await Deno.writeTextFile(argv.jsonFile, JSON.stringify(rows));

	if(argv.json)
	{
		console.log(JSON.stringify(rows));
		Deno.exit(0);
	}

	if(inputFilePaths)
		console.log(`${xu.colon(fg.peach("File"))} ${inputFilePath}`);
	const maxes =
	{
		matchType : rows.map(({matchType}) => (matchType || "").length).max(),
		family    : rows.map(({family}) => (family || "").length).max()
	};

	const printRows = rows.map(({from, family, confidence, magic, extensions, matchType, formatid, unsupported, weak}) => ({
		from : from==="dexvert" ? fg.green(from) : from,
		confidence,
		format : `${from!=="dexvert" ? magic.innerTruncate(75) : magic}${unsupported ? fg.deepSkyblue(" unsupported") : ""}${weak ? fg.deepSkyblue(" weak") : ""}`,
		extensions,
		dexvert : `${from!=="dexvert" ? "" : `${fg.peach(matchType.padStart(maxes.matchType))} ${fg.yellow(family.padStart(maxes.family))}${fg.cyan("/")}${fg.yellowDim(formatid)}`}`}));
	console.log(printUtil.columnizeObjects(printRows, {
		colNameMap : {confidence : "%"},
		color      : {confidence : "white"}}));
}
