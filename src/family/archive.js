import {Family} from "../Family.js";

export class archive extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		if(dexState.phase?.format?.verify && !(await dexState.phase.format.verify({dexState, dexFile})))
		{
			xlog.info`Archive failed format.verify() call`;
			return false;
		}

		return true;
	}
}
