import {xu} from "xu";
import {cmdUtil} from "xutil";
import {path, TextLineStream} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts any 'hex' dumps from ACX back into the binary equilivant.",
	args :
	[
		{argid : "inputFilePath", desc : "Input file to check", required : true},
		{argid : "outputDirPath", desc : "Output dir to write to", required : true}
	]});

const inputFile = await Deno.open(argv.inputFilePath);
let inHex = false;
const hexBytes = [];

for await(const line of inputFile.readable.pipeThrough(new TextDecoderStream()).pipeThrough(new TextLineStream()))
{
	if(inHex)
	{
		if(line.startsWith("===="))
			continue;

		const parts = line.split(" ").slice(2);
		parts.splice(8, 1);
		const hexParts = parts.slice(0, 16);
		if(hexParts.length!==16)
			continue;
		hexParts.filterInPlace(hexPart => hexPart!=="..");
		hexBytes.push(...hexParts.map(v => Number.parseInt(v, 16)));
	}
	else if(line.startsWith("Offset") && line.includes("Hex Data") && line.includes("Characters"))
	{
		inHex = true;
	}
	else
	{
		break;
	}
}

if(inHex && hexBytes.length>0)	// eslint-disable-line unicorn/prefer-ternary
	await Deno.writeFile(path.join(argv.outputDirPath, path.basename(argv.inputFilePath, ".txt")), Uint8Array.from(hexBytes));
else
	await Deno.copyFile(argv.inputFilePath, path.join(argv.outputDirPath, path.basename(argv.inputFilePath)));
