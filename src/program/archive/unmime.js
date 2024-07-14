import {Program} from "../../Program.js";
import {base64Decode, TextLineStream} from "std";

export class unmime extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	unsafe  = true;
	exec    = async r =>
	{
		let encodingType = null;
		let seenBlankLine = false;
		const encodedLines = [];
		for await(const line of (await Deno.open(r.inFile({absolute : true}))).readable.pipeThrough(new TextDecoderStream()).pipeThrough(new TextLineStream()))
		{
			if(line.toLowerCase().startsWith("content-transfer-encoding:"))
			{
				encodingType = line.split(":")[1].trim().toLowerCase();
				if(encodingType!=="base64")
				{
					r.xlog.warn`Unsupported encoding type: ${encodingType}`;
					break;
				}
				continue;
			}

			if(!line.trim()?.length)
			{
				seenBlankLine = true;
				continue;
			}

			if(seenBlankLine)
				encodedLines.push(line.trim());
		}

		const encodedData = encodedLines.join("").trim();
		if(encodedData?.length)
			await Deno.writeFile(await r.outFile(r.originalInput.name, {absolute : true}), base64Decode(encodedData));
	};
	renameOut = false;
}
