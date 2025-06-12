import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class nconvertID extends Program
{
	website    = "https://www.xnview.com/en/nconvert/";
	package    = "media-gfx/nconvert";
	bin        = "nconvert";
	loc        = "local";
	args       = r => ["-info", r.inFile()];
	runOptions = ({timeout : xu.SECOND*20});	// can take a while on bigger files, so just timeout quickly
	post       = r =>
	{
		// NOTE: nconvert DOES utilize the extension 'to some degree' to determine the format, but in my tests it didn't seem necessary to strip the extension a-la ffprobeID
		r.meta.detections = [];

		const meta = {};
		const lines = r.stdout.trim().split("\n").map(line => line.trim());
		for(const line of lines)
		{
			let {key, value} = line.match(/\s*(?<key>[^:]+):\s*(?<value>.+)/)?.groups || {};
			key = key?.trim()?.toLowerCase();
			value = value?.trim();

			if(!key?.length || !value?.length)
				continue;

			if(!["format", "name", "compression"].includes(key))
				continue;

			meta[key] = value;
		}

		if(meta.format && meta.name)
			r.meta.detections.push(Detection.create({value : `${meta.format} :${meta.name}:`, confidence : 100, from : "nconvertID", file : r.f.input}));
	};
	renameOut = false;
}
