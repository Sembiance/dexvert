import {Program} from "../../Program.js";

export class img2pdf extends Program
{
	website   = "https://pypi.org/project/img2pdf/";
	package   = "media-gfx/img2pdf";
	unsafe    = true;
	bin       = "img2pdf";
	args      = async r => [...r.inFiles(), "-o", await r.outFile("out.pdf")];
	renameOut = true;
}
