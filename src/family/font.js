import {Family} from "../Family.js";
import {Program} from "../Program.js";

export class font extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {identify} = await import("../identify.js");
		const identifications = await identify(dexFile, {xlog : xlog.clone("error")});

		// if it's an OTF, further validate it
		if(identifications.some(id => id.from==="dexvert" && id.family==="font" && id.formatid==="otf"))
		{
			const otfinfoR = await Program.runProgram("otfinfo", dexFile, {xlog, autoUnlink : true});
			if(!otfinfoR.meta?.family)
				return false;

			return {identifications};
		}

		return {identifications};
	}
}
