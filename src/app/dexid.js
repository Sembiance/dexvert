import {xu, fg} from "xu";
import {cmdUtil, printUtil, runUtil, fileUtil} from "xutil";
import {path} from "std";
import {DEXRPC_HOST, DEXRPC_PORT} from "../dexUtil.js";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexid",
	version : "1.0.0",
	desc    : "Identifies one or more files",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "warn"},
		json     : {desc : "Output JSON"},
		jsonFile : {desc : "If set, will output the result JSON to the given filePath", hasValue : true},
		fileMeta : {desc : "JSON representing extra meta info about this file. For example, a previous run of uniso[hfs] will output additional metadata about the files.", hasValue : true},
		direct   : {desc : "Skip going through the dex RPC server and directly load dexvert (still requires dexserver to be running, but allows debugging of src/dexvert.js"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "One or more file paths to identify", required : true, multiple : true}
	]});

const xlog = new XLog(argv.json && !argv.jsonFile ? "none" : argv.logLevel);

const tailProcs = [];
if(!argv.logFile && xlog.atLeast("debug"))
{
	tailProcs.push(await runUtil.run("tail", ["-n", "0", "-f", "/mnt/dexvert/log/dexserver.out"], {detached : true, liveOutput : true}));
	tailProcs.push(await runUtil.run("tail", ["-n", "0", "-f", "/mnt/dexvert/log/dexserver.err"], {detached : true, liveOutput : true}));
}

async function handleExit(ignored)
{
	await xlog.flush();
	await tailProcs.parallelMap(async o => await runUtil.kill(o.p));
	Deno.exit(0);
}

const inputFilePaths = Array.force(argv.inputFilePath);
for(const inputFilePath of inputFilePaths)
{
	if(!await fileUtil.exists(inputFilePath))
	{
		console.error(`File ${fg.cyan(inputFilePath)} does not exist`);
		continue;
	}
	
	let idMeta;
	let rows;
	if(argv.direct)
	{
		const {init : initPrograms} = await import(path.join(import.meta.dirname, "../program/programs.js"));
		const {init : initFormats} = await import(path.join(import.meta.dirname, "../format/formats.js"));

		await initPrograms();
		await initFormats();

		const {DexFile} = await import(path.join(import.meta.dirname, "../DexFile.js"));
		const {identify} = await import(path.join(import.meta.dirname, "../identify.js"));

		const inputFile = await DexFile.create(inputFilePath);
		if(argv.fileMeta)
			inputFile.meta = xu.parseJSON(argv.fileMeta);

		({ids : rows, idMeta} = await identify(inputFile, {xlog}));
	}
	else
	{
		const rpcData = {op : "dexid", inputFilePath : path.resolve(inputFilePath), logLevel : argv.logLevel, fileMeta : xu.parseJSON(argv.fileMeta)};
		const {r, log, err} = await xu.fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {json : rpcData, asJSON : true});
		if(err)
		{
			await handleExit();
			Deno.exit(console.error(`${log.join("\n")}\n${err}`.trim()));
		}

		if(!r && !log)
		{
			await handleExit();
			Deno.exit(console.error(`Failed to retrieve dexid data from dexrpc server. Is it running?`));
		}

		({ids : rows, idMeta} = r);

		if(log.length)
			console.log(log.join("\n"));
	}

	if(argv.jsonFile)
		await fileUtil.writeTextFile(argv.jsonFile, JSON.stringify(rows));

	if(argv.json)
	{
		console.log(JSON.stringify(rows));
		await handleExit();
		Deno.exit(0);
	}

	if(inputFilePaths)
		console.log(`${xu.colon(fg.peach("  File"))} ${inputFilePath}`);

	if(idMeta && Object.keys(idMeta)?.length)
		console.log(`${xu.colon(fg.orange("idMeta"))} ${printUtil.inspect(idMeta)}\n`);

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

await handleExit();
