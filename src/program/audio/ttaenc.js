import {Program} from "../../Program.js";

export class ttaenc extends Program
{
	website   = "https://tta.sourceforge.net";
	package   = "media-sound/ttaenc";
	bin       = "ttaenc";
	args      = r => ["-d", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = true;
	chain     = "sox[type:wav]";
}
