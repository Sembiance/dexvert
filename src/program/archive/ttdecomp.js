import {Program} from "../../Program.js";

export class ttdecomp extends Program
{
	website   = "http://www.exelana.com/techie/c/ttdecomp.html";
	package   = "app-arch/ttdecomp";
	bin       = "ttdecomp";
	args      = async r => [r.inFile(), await r.outFile("out")];
	renameOut = true;
}
