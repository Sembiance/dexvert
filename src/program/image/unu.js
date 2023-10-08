import {Program} from "../../Program.js";

export class unu extends Program
{
	website   = "https://teem.sourceforge.net/";
	package   = "sci-visualization/teem";
	bin       = "unu";
	args      = async r => ["save", "-f", "pnm", "-i", r.inFile(), "-o", await r.outFile("out.pnm")];
	renameOut = false;
	chain     = "convert";
}
