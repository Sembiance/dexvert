import {Program} from "../../Program.js";

export class pfsconvert extends Program
{
	website   = "http://pfstools.sourceforge.net/";
	package   = "media-gfx/pfstools";
	bin       = "pfsconvert";
	args      = async r => [r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
