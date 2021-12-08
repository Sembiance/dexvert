import {Family} from "../Family.js";
import {verifyAudio} from "./audio.js";

export class music extends Family
{
	async verify(dexState, dexFile)
	{
		return await verifyAudio(dexState, dexFile);
	}
}
