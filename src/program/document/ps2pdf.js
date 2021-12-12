import {Program} from "../../Program.js";

export class ps2pdf extends Program
{
	website   = "https://ghostscript.com/";
	package   = "app-text/ghostscript-gpl";
	unsafe    = true;
	bin       = "ps2pdf";
	args      = async r => [r.inFile(), await r.outFile("out.pdf")];
	renameOut = true;
}
