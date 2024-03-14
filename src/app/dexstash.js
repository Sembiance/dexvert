import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, runUtil, hashUtil} from "xutil";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexdeep",
	version : "1.0.0",
	desc    : "Stashes <inputFilePath>'s into test/sample/<family/format>>",
	opts    :
	{
		delete : {desc : "Delete the original file after stashing"},
		create : {desc : "Create the stash dir if it doesn't exist"},
		record : {desc : "Record the stashed file using test/testdexvert.js"}
	},
	args :
	[
		{argid : "familyFormat", desc : "The family/format to stash as", required : true},
		{argid : "inputFilePath", desc : "The path to the file to stash", required : true, multiple : true}
	]});

const xlog = new XLog("info");

const stashDirPath = path.join(import.meta.dirname, "..", "..", "test", "sample", argv.familyFormat);
if(!await fileUtil.exists(stashDirPath))
{
	if(!argv.create)
		Deno.exit(xlog.error`Invalid family/format: ${argv.familyFormat}`);
	
	await Deno.mkdir(stashDirPath, {recursive : true});
}

const existingSampleFilePaths = await fileUtil.tree(stashDirPath, {nodir : true, depth : 1});
const existingSampleSums = Object.fromEntries(await existingSampleFilePaths.parallelMap(async existingSampleFilePath => ([await hashUtil.hashFile("blake3", existingSampleFilePath), existingSampleFilePath])));
const longestInputFilePathLength = argv.inputFilePath.map(v => v.length).max();

for(const srcFilePath of argv.inputFilePath)
{
	const logPrefix = `${srcFilePath.padStart(longestInputFilePathLength)} ${fg.cyan("<---")}`;
	const sum = await hashUtil.hashFile("blake3", srcFilePath);
	if(existingSampleSums[sum])
	{
		xlog.info`${logPrefix} ${fg.orange("SKIPPED")} sample file already exists (${path.relative(stashDirPath, existingSampleSums[sum])})`;
		if(argv.delete)
			await fileUtil.unlink(srcFilePath);

		continue;
	}

	let destFilePath = path.join(stashDirPath, path.basename(srcFilePath));
	if(await fileUtil.exists(destFilePath))
	{
		destFilePath = await fileUtil.genTempPath(stashDirPath, path.extname(srcFilePath));
		xlog.info`${logPrefix}  ${fg.yellow("COPIED")} (duplicate filename exists, renamed to ${path.basename(destFilePath)})`;
	}
	else
	{
		xlog.info`${logPrefix}  ${fg.yellow("COPIED")}`;
	}

	existingSampleSums[sum] = destFilePath;

	// we use rsync to preserve file date/time
	await runUtil.run("rsync", runUtil.rsyncArgs(srcFilePath, destFilePath, {fast : true}));
	await runUtil.run("chmod", ["644", destFilePath]);

	if(argv.delete)
		await fileUtil.unlink(srcFilePath);

	if(argv.record)
		await runUtil.run("deno", runUtil.denoArgs(path.join(import.meta.dirname, "..", "..", "test", "testdexvert.js"), "--record", `--format=${argv.familyFormat}`, `--file=${path.basename(destFilePath)}`), runUtil.denoRunOpts({liveOutput : true}));
}

xlog.info`\n# Samples: ${(await fileUtil.tree(stashDirPath, {nodir : true, depth : 1})).length.toLocaleString()}`;
