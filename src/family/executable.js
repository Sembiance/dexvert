import {Family} from "../Family.js";

export class executable extends Family
{
	async verify(dexState, dexFile)	// eslint-disable-line no-unused-vars, require-await
	{
		return true;
	}
}
