import {Program} from "../../Program.js";

export class dvi2pdf extends Program
{
	website   = "http://tug.org/texlive/";
	package   = "app-text/texlive";
	unsafe    = true;
	bin       = "dvips";
	args      = async r => ["-o", await r.outFile("out.ps"), r.inFile()];
	renameOut = true;
	chain     = "ps2pdf";
}
