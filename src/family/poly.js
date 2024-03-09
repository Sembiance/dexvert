import {Family} from "../Family.js";
import {Program} from "../Program.js";

export class poly extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {identify} = await import("../identify.js");
		const identifications = await identify(dexFile, {xlog : xlog.clone("error")});

		// if it's not a glTF, fail
		if(!identifications.some(id => id.from==="dexvert" && id.family==="poly" && id.formatid==="glTF"))
		{
			xlog.warn`DELETING OUTPUT due to not being identified as a glTF: ${dexFile.pretty()}`;
			return false;
		}

		// If it is a glTF, we need to confirm it's a "real" glTF file:
		const assimpInfoR = await Program.runProgram("assimpInfo", dexFile, {xlog, autoUnlink : true});
		if(!assimpInfoR.meta.vertices)
		{
			xlog.warn`Poly failed verification due to not detecting any vertices: ${assimpInfoR.meta}`;
			return false;
		}

		return {identifications, meta : assimpInfoR.meta};
	}
}
