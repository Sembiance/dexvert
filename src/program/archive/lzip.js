import {xu} from "xu";
import {Program} from "../../Program.js";

export class lzip extends Program
{
	website   = "https://www.nongnu.org/lzip/lzip.html";
	package   = "app-arch/lzip";
	bin       = "lzip";
	args      = async r => ["-d", "-k", "-o", await r.outFile("outfile"), r.inFile()];
	renameOut = true;
}
