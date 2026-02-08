import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {identify} from "../identify.js";

export class poly extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {ids : identifications} = (await identify(dexFile)) || {};

		// if it's not a glTF, fail
		if(!identifications?.some(id => id.from==="dexvert" && id.family==="poly" && id.formatid==="glTF"))
		{
			xlog.warn`DELETING OUTPUT due to not being identified as a glTF: ${dexFile.pretty()}`;
			return false;
		}

		// If it is a glTF, we need to confirm it's a "real" glTF file:
		const polyInfo = {};
		for(const progid of ["glTFValidator", "assimpInfo"])
			Object.assign(polyInfo, (await Program.runProgram(progid, dexFile, {xlog, autoUnlink : true}))?.meta || {});

		if(!polyInfo?.vertices)
		{
			xlog.warn`DELETING OUTPUT due to Poly verification failure due to not detecting any vertices: ${polyInfo}`;
			return false;
		}

		return {identifications, meta : polyInfo};
	}
}
