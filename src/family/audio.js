import {xu} from "xu";
import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {runUtil} from "xutil";

export async function verifyAudio(dexState, dexFile, identifications)
{
	const xlog = dexState.xlog;
	const dexid = identifications.find(id => id.from==="dexvert" && id.family==="audio" && id.formatid==="mp3");
	if(!dexid)
	{
		xlog.warn`DELETING OUTPUT due to not being identified as audio/mp3: ${dexFile.pretty()}`;
		return false;
	}

	const r = await Program.runProgram("soxi", dexFile, {xlog});
	await r.unlinkHomeOut();
	if(!r.meta.sampleEncoding)
	{
		xlog.warn`Audio failed verification due to not detecting a sample encoding: ${r.meta}`;
		return false;
	}

	// Used to use here `sox <file> -n stat` (see sandbox/legacy/soxStat.txt) but that isn't reliable for very short MP3s such as those from gusPatch/VIOLIN.PAT
	// I could use `mplayer -identify -nocache -vo null -ao null <file>` or `ffmpeg -i <file>` to try and detect duration/etc

	return true;
}

export class audio extends Family
{
	async verify(dexState, dexFile, identifications)
	{
		return await verifyAudio(dexState, dexFile, identifications);
	}
}
