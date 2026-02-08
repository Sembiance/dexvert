import {Family} from "../Family.js";
import {videoUtil} from "xutil";
import {identify} from "../identify.js";

export class video extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {ids : identifications} = await identify(dexFile);
		const dexid = identifications.find(id => id.from==="dexvert" && id.family==="video" && id.formatid==="mp4");
		if(!dexid)
		{
			xlog.warn`DELETING OUTPUT due to not being identified as video/mp4: ${dexFile.pretty()}`;
			return false;
		}

		const videoInfo = await videoUtil.getInfo(dexFile.absolute);
		if(!videoInfo.width || !videoInfo.height)
		{
			xlog.warn`Video failed verification due to not detecting width or height ${videoInfo}`;
			return false;
		}

		return {meta : videoInfo};
	}

	// gets meta information for the given input and format
	async meta(inputFile, format)
	{
		if(!format.metaProvider)
			return;

		const meta = {};
		for(const metaProvider of format.metaProvider)
		{
			// mplayer meta provider
			if(metaProvider==="mplayer")
				Object.assign(meta, await videoUtil.getInfo(inputFile.absolute));
		}

		return meta;
	}
}
