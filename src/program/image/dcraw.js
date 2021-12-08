import {Program} from "../../Program.js";

export class dcraw extends Program
{
	website       = "https://www.cybercom.net/~dcoffin/dcraw/";
	package       = "media-gfx/dcraw";
	bin           = "dcraw";
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	chain         = "convert";
}
