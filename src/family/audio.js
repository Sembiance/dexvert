import {xu} from "xu";
import {Family} from "../Family.js";
import {Program} from "../Program.js";

export class audio extends Family
{
	async verify(dexState, dexFile, identifications)
	{
		const xlog = dexState.xlog;
		const dexid = identifications.find(id => id.from==="dexvert" && id.family==="audio" && id.formatid==="mp3");
		if(!dexid)
		{
			xlog.warn`DELETING OUTPUT due to not being identified as audio/mp3: ${dexFile.pretty()}`;
			return false;
		}

		const r = await Program.runProgram("soxi", dexFile, {xlog});
		await r.unlinkHomeOut();
		if(!r.meta.sampleEncoding)
		{
			xlog.warn`Audio failed verification due to not detecting a sample encoding: ${r.meta}`;
			return false;
		}

		return true;
	}

	// gets meta information for the given input and format
	async meta(inputFile, format, xlog)
	{
		if(!format.metaProvider)
			return;

		const meta = {};
		for(const metaProvider of format.metaProvider)
		{
			xlog.info`Getting meta from provider ${metaProvider}`;

			const r = await Program.runProgram(metaProvider, inputFile, {xlog});
			if(r.meta)
				Object.assign(meta, r.meta);
			await r.unlinkHomeOut();
		}

		return meta;
	}
}
