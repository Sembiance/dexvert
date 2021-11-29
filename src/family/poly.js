import {Family} from "../Family.js";

export class poly extends Family
{
	async verify(dexState, dexFile, identifications)	// eslint-disable-line no-unused-vars, require-await
	{
		return true;
	}
}
