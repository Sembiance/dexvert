import {xu} from "xu";
import {Program} from "../../Program.js";

export class macDrawPICTExtract extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = "python3";
	args      = async r => [Program.binPath("macDrawPICTExtract.py"), r.inFile(), await r.outFile("out.pict")];
	renameOut = true;
	chain     = "dexvert[asFormat:image/pict]";
}
