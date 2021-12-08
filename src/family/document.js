import {Family} from "../Family.js";

export class document extends Family
{
	async verify(dexState, dexFile)	// eslint-disable-line no-unused-vars, require-await
	{
		return true;
	}
}
