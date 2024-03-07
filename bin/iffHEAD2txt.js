import {xu} from "xu";
import {read as readIFF} from "./iffUtil.js";
import {cmdUtil, encodeUtil, fileUtil} from "xutil";
import {XLog} from "xlog";

const xlog = new XLog("info");

// SPECIFICATION: https://wiki.amigaos.net/wiki/HEAD_IFF_Flow_Idea_Processor_Format

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <input> from iff HEAD to <output.txt>",
	args :
	[
		{argid : "inputFilePath", desc : "IFF HEAD file path to convert", required : true},
		{argid : "outputFilePath", desc : "Output file to write to", required : true}
	]});

const iff = await readIFF(argv.inputFilePath);
if(iff.type!=="FORM" || iff.formType!=="HEAD")
	Deno.exit(xlog.error`Error: IFF file does not start with the expected FORM HEAD`);

if(iff.chunks.some(chunk => !["NEST", "TEXT", "FSCC"].includes(chunk.type)))
	Deno.exit(xlog.error`Error: IFF file does not contain the expected NEST, TEXT and FSCC chunks`);

const r = [];
let indent = 0;
for(const chunk of iff.chunks)
{
	if(chunk.type==="NEST")
	{
		indent = chunk.data.getUInt16LE();
		continue;
	}

	if(chunk.type==="FSCC")
		continue;

	if(chunk.type==="TEXT")
		r.push(`${"    ".repeat(indent)}${await encodeUtil.decode(chunk.data, "ISO-8859-1")}`);
}

await fileUtil.writeTextFile(argv.outputFilePath, r.join("\n"));
