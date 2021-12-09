import {xu} from "xu";
import {Format} from "../../Format.js";
import {Program} from "../../Program.js";
import {runUtil} from "xutil";

export class cue extends Format
{
	name         = "ISO CUE Sheet";
	website      = "http://fileformats.archiveteam.org/wiki/CUE_and_BIN";
	ext          = [".cue"];
	metaProvider = ["text"];
	magic        = ["ISO CDImage cue", "Cue Sheet"];
	untouched    = dexState => !!dexState.meta.cue;
	meta         = async (inputFile, dexState) =>
	{
		const {stdout : cueDataRaw} = await runUtil.run(Program.binPath("parseCUE/parseCUE.js"), [inputFile.absolute]);
		const cueData = xu.parseJSON(cueDataRaw, {});
		if(Object.keys(cueData).length===0)
			return;
		
		Object.keys(cueData).forEach(k =>
		{
			if(cueData[k]===null)
				delete cueData[k];
		});

		Object.keys(cueData.track || {}).forEach(k =>
		{
			if(cueData.track[k]===null)
				delete cueData.track[k];
		});
		
		cueData.files.flatMap(file => file.tracks || []).forEach(track =>
		{
			Object.keys(track).forEach(k =>
			{
				if(track[k]===null)
					delete track[k];
			});
		});

		dexState.meta.cue = cueData;
	};
}
