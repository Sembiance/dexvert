import {xu} from "xu";
import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {rpcidentify} from "../identify.js";

export async function verifyAudio(dexState, dexFile)
{
	const xlog = dexState.xlog;
	const identifications = await rpcidentify(dexFile);
	if(!identifications.some(id => id.from==="dexvert" && id.family==="audio" && id.formatid==="mp3"))
	{
		xlog.warn`DELETING OUTPUT due to not being identified as audio/mp3: ${dexFile.pretty()}`;
		return false;
	}

	const soxiR = await Program.runProgram("soxi", dexFile, {xlog, autoUnlink : true});
	if(!soxiR.meta.sampleEncoding)
	{
		xlog.warn`Audio failed verification due to not detecting a sample encoding: ${soxiR.meta}`;
		return false;
	}

	// So sox isn't reliable at providing a stat for very short clips, so we use ffprobe to get duration of the MP3 and only get sox stat if duration>=2 seconds
	// Alternative duration getters: `mplayer -identify -nocache -vo null -ao null <file>` or `ffmpeg -i <file>`
	const ffprobeR = await Program.runProgram("ffprobe", dexFile, {xlog, autoUnlink : true});
	if((ffprobeR.meta?.duration || 0)>=(xu.SECOND*2))
	{
		const {meta : soxStat} = await Program.runProgram("soxStat", dexFile, {xlog, autoUnlink : true});
		if(soxStat["sox FAIL formats"] || (soxStat["Maximum amplitude"]==="0.000000" && soxStat["Minimum amplitude"]==="0.000000" && soxStat["Midline amplitude"]==="0.000000"))
		{
			xlog.warn`Audio verification failed due to invalid sox stat ${soxStat}`;
			return false;
		}
	}

	return {identifications, meta : ffprobeR.meta};
}

export class audio extends Family
{
	async verify(dexState, dexFile)
	{
		return await verifyAudio(dexState, dexFile);
	}
}
