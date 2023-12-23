import {Program} from "../../Program.js";

export class arj extends Program
{
	website   = "https://arj.sourceforge.net/";
	package   = "app-arch/arj";
	bin       = "arj";
	args      = r => ["x", r.inFile(), r.outDir()];
	renameOut = false;
}
