import {Program} from "../../Program.js";

export class pdf2svg extends Program
{
	website   = "https://github.com/dawbarton/pdf2svg/";
	package   = "media-gfx/pdf2svg";
	bin       = "pdf2svg";
	args      = async r => [r.inFile(), await r.outFile("out.svg")];
	chain     = "deDynamicSVG[autoCrop]";
	renameOut = true;
}
