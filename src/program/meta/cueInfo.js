import {xu} from "xu";
import {Program} from "../../Program.js";

export class cueInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	bin     = Program.binPath("cueInfo/cueInfo.js");
	args    = r => ["--", r.inFile()];
	post    = r =>
	{
		const cueData = xu.parseJSON(r.stdout, {});
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

		Object.assign(r.meta, cueData);
	};
	renameOut = false;
}
