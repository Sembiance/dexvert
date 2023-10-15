import {xu, fg} from "xu";
import {cmdUtil, printUtil, fileUtil} from "xutil";
import {path} from "std";
import {DEXRPC_HOST, DEXRPC_PORT} from "../server/dexrpc.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexid",
	version : "1.0.0",
	desc    : "Identifies one or more files",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "warn"},
		json     : {desc : "Output JSON"},
		jsonFile : {desc : "If set, will output the result JSON to the given filePath", hasValue : true},
		fileMeta : {desc : "JSON representing extra meta info about this file. For example, a previous run of uniso[hfs] will output additional metadata about the files.", hasValue : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "One or more file paths to identify", required : true, multiple : true}
	]});

const inputFilePaths = Array.force(argv.inputFilePath);
for(const inputFilePath of inputFilePaths)
{
	if(!await fileUtil.exists(inputFilePath))
	{
		console.error(`File ${fg.cyan(inputFilePath)} does not exist`);
		continue;
	}
	
	const rpcData = {op : "dexid", inputFilePath : path.resolve(inputFilePath), logLevel : argv.logLevel, fileMeta : xu.parseJSON(argv.fileMeta)};
	const {r : rows, logLines} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(rpcData)}))?.json()), {});
	if(!rows && !logLines)
		Deno.exit(console.error(`Failed to contact dexserver at ${fg.cyan(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`)} is it running?`));
	
	if(logLines.length)
		console.log(logLines.join("\n"));

	if(argv.jsonFile)
		await fileUtil.writeTextFile(argv.jsonFile, JSON.stringify(rows));

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
