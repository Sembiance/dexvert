import {Program} from "../../Program.js";

export class ps2pdf extends Program
{
	website = "https://ghostscript.com/";
	package = "app-text/ghostscript-gpl";
	flags   = {
		fromEPS : "Source image is an EPS",
		svg     : "Set this flag to treat the PS as an image and convert to SVG"
	};
	unsafe     = true;
	bin        = "ps2pdf";
	args       = async r => [...(r.flags.fromEPS ? ["-dEPSCrop"] : []), r.inFile(), await r.outFile("out.pdf")];
	renameOut  = true;
	chain      = "?pdf2svg";
	chainCheck = r => r.flags.svg;
}
