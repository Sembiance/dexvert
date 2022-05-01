import {xu} from "xu";
import {fileUtil} from "xutil";
import {Family} from "../Family.js";
import {Program} from "../Program.js";

export class text extends Family
{
	// gets meta information for the given input and format
	async meta(inputFile, format, xlog)
	{
		if(!format.metaProvider)
			return;

		const meta = {};
		for(const metaProvider of format.metaProvider)
		{
			xlog.info`Getting meta from provider ${metaProvider}`;

			if(metaProvider==="text")
			{
				let lineCount = 0;

				// if 20MB or less, read it in and count the newlines here, it's more accurate than 'wc' when dealing with utf-8
				if(inputFile.size<xu.MB*20)
				{
					const textRaw = await fileUtil.readTextFile(inputFile.absolute);
					lineCount = textRaw.split(textRaw.includes("\n") ? "\n" : "\r").length;
				}
				
				// fallback to wc if needed
				if(!lineCount)
				{
					const wcR = await Program.runProgram("wc", inputFile, {xlog, autoUnlink : true});
					lineCount = wcR.meta?.lineCount;

					// wc undercounts by 1 if the last byte isn't a new line, check and fix that here
					const f = await Deno.open(inputFile.absolute);
					await Deno.seek(f.rid, -1, 2);
					const buf = new Uint8Array(1);
					await Deno.read(f.rid, buf);
					Deno.close(f.rid);
					if(buf[0]!==0x0A && buf[0]!==0x0D)
						lineCount++;
				}
				
				if(!lineCount)
					return;

				const textMeta = {lineCount, charSet : {}};
				if(format.charSet)
					textMeta.charSet.declared = format.charSet;
				
				// detect our charSet
				const chardetectR = await Program.runProgram("chardetect", inputFile, {xlog, autoUnlink : true});
				if(chardetectR.meta?.charSet)
					textMeta.charSet.detected = chardetectR.meta.charSet;

				if(Object.keys(textMeta.charSet).length===0)
					delete textMeta.charSet;

				Object.assign(meta, textMeta);
			}
		}

		return meta;
	}
}
