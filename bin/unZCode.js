import {xu} from "xu";
import {cmdUtil, runUtil, fileUtil} from "xutil";
import {TextLineStream} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts any ZCode using txd but filters out the code sections.",
	args :
	[
		{argid : "inputFilePath", desc : "Input file to process", required : true},
		{argid : "outputFilePath", desc : "Output file to write", required : true}
	]});

const txdOutFilePath = await fileUtil.genTempPath(undefined, ".txt");
await runUtil.run("txd", [argv.inputFilePath], {stdoutFilePath : txdOutFilePath});

if(!await fileUtil.exists(txdOutFilePath) || (await Deno.stat(txdOutFilePath)).size===0)
	Deno.exit(await fileUtil.unlink(txdOutFilePath));

const encoder = new TextEncoder();
const outputFile = await Deno.open(argv.outputFilePath, {create : true, write : true, truncate : true});
const inputFile = await Deno.open(txdOutFilePath);
let skip = false;
for await (const line of inputFile.readable.pipeThrough(new TextDecoderStream()).pipeThrough(new TextLineStream()))
{
	if(line.startsWith("[Start of code]"))
	{
		skip = true;
		continue;
	}

	if(line.startsWith("[End of code]"))
	{
		skip = false;
		continue;
	}

	if(skip)
		continue;
	
	await new Blob([encoder.encode(line + "\n")]).stream().pipeTo(outputFile.writable, {preventClose : true});	// eslint-disable-line prefer-template
}

outputFile.close();
inputFile.close();

await fileUtil.unlink(txdOutFilePath);
