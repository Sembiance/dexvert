import {xu} from "xu";
import {Family} from "../Family.js";
import {verifyAudio} from "./audio.js";

export class music extends Family
{
	async verify(dexState, dexFile)
	{
		const verification = await verifyAudio(dexState, dexFile);

		// if we have a duration and it's less than 0.1 seconds (100ms), fail validation
		if(verification?.meta?.duration && verification.meta.duration<100)
			return false;

		return verification;
	}
}
