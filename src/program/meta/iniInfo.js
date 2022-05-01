import {xu} from "xu";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";

export class iniInfo extends Program
{
	website   = "https://github.com/Sembiance/inivalidate";
	package   = "app-arch/inivalidate";
	bin       = "inivalidate";
	args      = r => [r.inFile()];
	post      = async r =>
	{
		const meta = xu.parseJSON(r.stdout, {});
		
		// if we are not valid or have no section names, we don't assign meta
		if(!meta.valid || !meta.sectionNames)
			return;
		
		// if INI file is <20MB, do some additional checking
		if(r.f.input.size<xu.MB*20)
		{
			// some INI file sections have periods at the start or end, which libconfini trims, so we handle that check here and return if any are not found which is usually because it's not an actual INI file
			const iniRaw = await fileUtil.readTextFile(r.f.input.absolute);
			if(iniRaw && meta.sectionNames.some(sectionName => sectionName && (!iniRaw.includes(`[${sectionName}`) && !iniRaw.includes(`${sectionName}]`))))
				return;
		}

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
