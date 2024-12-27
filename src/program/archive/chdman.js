import {Program} from "../../Program.js";

export class chdman extends Program
{
	website   = "https://github.com/mamedev/mame/releases";
	package   = "games-emulation/mame-tools";
	bin       = "chdman";
	args      = async r => ["extracthd", "-i", r.inFile(), "-o", await r.outFile("out.img")];
	renameOut = true;
}
