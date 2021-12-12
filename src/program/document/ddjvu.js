import {Program} from "../../Program.js";

export class ddjvu extends Program
{
	website   = "http://djvu.sourceforge.net/";
	package   = "app-text/djvu";
	bin       = "ddjvu";
	args      = async r => ["-format=pdf", r.inFile(), await r.outFile("out.pdf")];
	renameOut = true;
}
