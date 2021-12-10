import {Program} from "../../Program.js";

export class smus2midi extends Program
{
	website   = "https://github.com/AugusteBonnin/smus2midi";
	package   = "media-sound/smus2midi";
	bin       = "smus2midi";
	cwd       = r => r.outDir();
	args      = r => [r.inFile()];
	renameOut = true;
	chain     = "timidity";
}
