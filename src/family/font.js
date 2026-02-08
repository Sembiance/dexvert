import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {identify} from "../identify.js";

export class font extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {ids : identifications} = await identify(dexFile);

		// if it's an OTF, further validate it
		if(identifications.some(id => id.from==="dexvert" && id.family==="font" && id.formatid==="otf"))
		{
			const otfinfoR = await Program.runProgram("otfinfo", dexFile, {xlog, autoUnlink : true});
			if(!otfinfoR.meta?.family && !otfinfoR.meta?.subfamily && !otfinfoR.meta?.fullName && !otfinfoR.meta?.postScriptName)
				return false;

			return {identifications};
		}

		return {identifications};
	}
}
