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

	// So sox isn't reliable at providing a stat for clips under 1 second, so we use ffprobe to get duration of the MP3 and only get sox stat if duration>=1 second
	// Alternative duration getters: `mplayer -identify -nocache -vo null -ao null <file>` or `ffmpeg -i <file>`
	const ffprobeR = await Program.runProgram("ffprobe", dexFile, {xlog});
	await ffprobeR.unlinkHomeOut();
	if((ffprobeR.meta?.duration || 0)>=1)
	{
		const {stderr} = await runUtil.run("sox", [dexFile.rel, "-n", "stat"], {cwd : dexFile.root});
		const soxStat = stderr.trim().split("\n").reduce((result, line="") =>	// eslint-disable-line unicorn/prefer-object-from-entries
		{
			const parts = line.split(":");
			if(!parts || parts.length!==2)
				return result;
			result[parts[0].split(" ").filter(v => !!v).map(v => v.trim()).join(" ")] = parts[1].trim();
			return result;
		}, {});
		
		if(soxStat["sox FAIL formats"] || (soxStat["Maximum amplitude"]==="0.000000" && soxStat["Minimum amplitude"]==="0.000000" && soxStat["Midline amplitude"]==="0.000000"))
		{
			xlog.warn`Audio verification failed due to invalid sox stat ${soxStat}`;
			return false;
		}
	}

	return true;
}

export class audio extends Family
{
	async verify(dexState, dexFile, identifications)
	{
		return await verifyAudio(dexState, dexFile, identifications);
	}
}
