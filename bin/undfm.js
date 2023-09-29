import {xu} from "xu";
import {cmdUtil} from "xutil";
import {path, TextLineStream} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Extracts data from <input.txt> decompiled Borland Delphi Forms and outputs image data into <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "Input DFM file to parse", required : true},
		{argid : "outputDirPath", desc : "Output dir to write to", required : true}
	]});

const outputFilePath = path.join(argv.outputDirPath, path.basename(argv.inputFilePath));
const outputFile = await Deno.open(outputFilePath, {create : true, write : true, truncate : true});
const encoder = new TextEncoder();

const inputFile = await Deno.open(argv.inputFilePath);
let imageType = null;
let imageCounter=0;
let inImage = false;
const hexBytes = [];
for await(const line of await inputFile.readable.pipeThrough(new TextDecoderStream()).pipeThrough(new TextLineStream()))
{
	if(inImage)
	{
		const lastLine = line.trim().endsWith("}");
		const hexData = lastLine ? line.trim().slice(0, -1) : line.trim();
		hexBytes.push(...hexData.split("").chunk(2).map(v => Number.parseInt(v.join(""), 16)));
		if(lastLine)
		{
			inImage = false;
			const uintData = Uint8Array.from(hexBytes);
			let offset = 0;
			const subType = uintData.getPascalString(0);
			let ext = `.unknown`;
			if(subType.length>0)
			{
				offset += 1+subType.length;
				switch(subType)
				{
					case "TBitmap":
						ext = ".bmp";
						offset += 4;
						break;
					
					case "TJPEGImage":
						ext = ".jpg";
						offset += 4;
						break;

					case "TGIFImage":
						ext = ".gif";
						offset += 4;
						break;

					case "TIcon":
						ext = ".ico";
						break;
					
					default:
						console.log(`UNKNOWN subType: ${subType}`);
						ext = `.${subType}`;
				}
			}
			else if(imageType==="Icon")
			{
				ext = ".ico";	// icon doesn't have any subType and so we just output directly to disk
			}

			const imageFilePath = path.join(argv.outputDirPath, `image${imageCounter.toString().padStart(3, "0")}${ext}`);
			await new Blob([encoder.encode(`<${path.basename(imageFilePath)}>}\n`)]).stream().pipeTo(outputFile.writable, {preventClose : true});

			await Deno.writeFile(imageFilePath, Uint8Array.from(uintData.subarray(offset)));
			imageCounter++;
		}
	}
	else if((/^Picture|Icon\.Data = {$/).test(line.trim()))
	{
		imageType = line.trim().split(".")[0];
		await new Blob([encoder.encode(line)]).stream().pipeTo(outputFile.writable, {preventClose : true});
		hexBytes.clear();
		inImage = true;
	}
	else
	{
		await new Blob([encoder.encode(`${line}\n`)]).stream().pipeTo(outputFile.writable, {preventClose : true});
	}
}

outputFile.close();
