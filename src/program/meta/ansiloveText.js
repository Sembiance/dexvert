import {xu} from "xu";
import {Program} from "../../Program.js";

export class ansiloveText extends Program
{
	website = "https://www.ansilove.org/";
	package = "media-gfx/ansilove";
	bin     = "ansilove";
	args    = r => ["-x", r.inFile()];
	post    = r =>
	{
		r.meta.imageText = r.stdout.replaceAll(/\s+/g, " ").trim();
		if(!r.meta.imageText?.length)
			delete r.meta.imageText;
	};
	renameOut = false;
}
