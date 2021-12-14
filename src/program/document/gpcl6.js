import {Program} from "../../Program.js";

export class gpcl6 extends Program
{
	website   = "https://www.ghostscript.com/download/gpcldnld.html";
	package   = "app-text/ghostpcl-bin";
	unsafe    = true;
	bin       = "gpcl6";
	args      = async r => [`-sOutputFile=${await r.outFile("out.pdf")}`, "-sDEVICE=pdfwrite", "-dNOPAUSE", r.inFile()];
	renameOut = true;
}
