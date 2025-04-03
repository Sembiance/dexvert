import {Program} from "../../Program.js";

export class sng extends Program
{
	website       = "https://sng.sourceforge.net/";
	package       = "media-gfx/sng";
	bin           = "sng";
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	renameOut     = true;
}
