import {xu} from "xu";
import {Program} from "../../Program.js";

export class swfdump extends Program
{
	website    = "http://www.swftools.org/";
	package    = "media-gfx/swftools";
	notes      = "Right now I only get frame rate from it. If I need more, I can add more in future.";
	bin        = "swfdump";
	args       = r => ["--rate", r.inFile()];
	post       = r =>
	{
		const frameRate = r.stdout.trim().match(/-r (?<rate>\d.+)/)?.groups?.rate;
		if(frameRate)
			r.meta.frameRate = +frameRate;
	};
	renameOut = false;
}
