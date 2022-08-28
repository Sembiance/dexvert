import {xu} from "xu";
import {path} from "std";
import {cmdUtil, runUtil, fileUtil} from "xutil";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexall",
	version : "1.0.0",
	desc    : "Dexverts one or more files",
	opts    :
	{
		outputDir : {desc : "Output directory. Default: /home/sembiance/tmp/out", hasValue : true, defaultValue : "/home/sembiance/tmp/out"}
	},
	args :
	[
		{argid : "inputFiles", desc : "Which files to convert", required : true, multiple : true}
	]});

const outputDirPath = path.resolve(path.relative(Deno.cwd(), argv.outputDir));
await fileUtil.unlink(outputDirPath, {recursive : true});
await Deno.mkdir(outputDirPath, {recursive : true});

await argv.inputFiles.parallelMap(async inputFile =>
{
	const inputFilePath = path.resolve(path.relative(Deno.cwd(), inputFile));
	const outputSubDirPath = path.join(outputDirPath, path.basename(inputFilePath));
	await Deno.mkdir(outputSubDirPath, {recursive : true});
	await runUtil.run("deno", runUtil.denoArgs("--allow-all", "/mnt/compendium/DevLab/dexvert/src/app/dexvert.js", inputFilePath, outputSubDirPath), runUtil.denoRunOpts());
});
