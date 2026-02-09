import {Program} from "../../Program.js";
import {xmlParse} from "denoLandX";

export class lsdvd extends Program
{
	website = "https://sourceforge.net/projects/lsdvd/";
	package = "media-video/lsdvd";
	bin     = "lsdvd";
	args    = r => ["-q", "-Ox", r.inFile()];
	post    = r =>
	{
		if(!r.stdout.trim().startsWith("<?xml"))
			return;

		for(const [k, v] of Object.entries(xmlParse(r.stdout.trim())?.lsdvd || {}))
			r.meta[k.toCamelCase()] = v;
	};
	renameOut = false;
}
