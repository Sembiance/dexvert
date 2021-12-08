import {Family} from "../Family.js";

export class archive extends Family
{
	async verify(dexState, dexFile, identifications)
	{
		const xlog = dexState.xlog;
		if(dexState.phase?.format?.verify && !(await dexState.phase.format.verify({dexState, dexFile, identifications})))
		{
			xlog.info`Archive failed format.verify() call`;
			return false;
		}

		return true;
	}
}
