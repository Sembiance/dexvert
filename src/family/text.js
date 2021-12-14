import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {TEXT_MAGIC} from "../Detection.js";

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

			// imageMagick meta provider
			if(metaProvider==="text")
			{
				const wcR = await Program.runProgram("wc", inputFile, {xlog, autoUnlink : true});
				const lineCount = wcR.meta?.lineCount;
				if(!lineCount)
					return;

				const textMeta = {lineCount, charSet : {}};
				if(this.charSet)
					textMeta.charSet.declared = this.charSet;
				
				// detect our charSet
				const chardetectR = await Program.runProgram("chardetect", inputFile, {xlog, autoUnlink : true});
				if(chardetectR.meta?.charSet)
					textMeta.charSet.detected = chardetectR.meta.charSet;

				if(Object.keys(textMeta.charSet).length===0)
					delete textMeta.charSet;
				
				// detect whether we are verified as text
				const fileR = await Program.runProgram("file", inputFile, {xlog, autoUnlink : true});

				const {flexMatch} = await import("../identify.js");	// need to import this dynamically to avoid circular dependency
				if(fileR.meta.detections.map(v => v.value).some(v => TEXT_MAGIC.some(m => flexMatch(v.trimChars(",").trim(), m))))
					textMeta.verifiedAsText = true;

				Object.assign(meta, textMeta);
			}
		}

		return meta;
	}
}
