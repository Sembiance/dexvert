import {Family} from "../Family.js";
import {verifyAudio} from "./audio.js";

export class music extends Family
{
	async verify(dexState, dexFile, identifications)
	{
		return await verifyAudio(dexState, dexFile, identifications);
	}
}
