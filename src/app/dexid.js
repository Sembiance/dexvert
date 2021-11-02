import {xu} from "xu";
import {cmdUtil, fileUtil, printUtil} from "xutil";
import {identify} from "../identify.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexid",
	version : "1.0.0",
	desc    : "Identifies one or more files",
	opts    :
	{
		verbose  : {desc : "Show additional info when identifying"},
		json     : {desc : "Output JSON"},
		jsonFile : {desc : "If set, will output the result JSON to the given filePath", hasValue : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "One or more file paths to identify", required : true, multiple : true}
	]});

for(const inputFilePath of Array.force(argv.inputFilePath))
{
	const rows = await identify(inputFilePath, {verbose : argv.verbose});

	if(argv.jsonFile)
		await fileUtil.writeFile(argv.jsonFile, JSON.stringify(rows));

	if(argv.json)
	{
		console.log(JSON.stringify(rows));	// eslint-disable-line no-restricted-syntax
		Deno.exit(0);
	}

	const printRows = rows.map(({from, family, confidence, magic, extensions, matchType, formatid}) => ({
		from : from==="dexvert" ? xu.cf.fg.green(from) : from,
		confidence,
		format : `${from!=="dexvert" ? magic.innerTruncate(100) : magic}${from==="dexvert" ? ` ${xu.cf.fg.peach(matchType)} ${xu.cf.fg.yellow(family)}${xu.cf.fg.cyan("/")}${xu.cf.fg.yellowDim(formatid)}` : ""}`,
		extensions}));
	console.log(printUtil.columnizeObjects(printRows, {		// eslint-disable-line no-restricted-syntax
		colNameMap : {confidence : "%"},
		color      : {confidence : "white"}}));
}
