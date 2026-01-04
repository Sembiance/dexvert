import {xu} from "xu";
import {Program} from "../../Program.js";

export class mmf2mid extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = Program.binPath("mmf2mid/mmf2mid.js");
	args      = async r => [r.inFile(), await r.outFile("out.mid")];
	renameOut = true;
}
