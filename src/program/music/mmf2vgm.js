import {xu} from "xu";
import {Program} from "../../Program.js";

export class mmf2vgm extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = Program.binPath("mmf2vgm.js");
	args      = async r => [r.inFile(), await r.outFile("out.vgm")];
	renameOut = true;
}
