import {xu} from "xu";
import {Program} from "../../Program.js";

export class stripGarbage extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = Program.binPath("stripGarbage/stripGarbage");
	args      = async r => ["--null", r.inFile(), await r.outFile("out.txt")];
	renameOut = true;
}
