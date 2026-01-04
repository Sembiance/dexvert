import {Program} from "../../Program.js";

export class astridAACDEC extends Program
{
	website   = "https://web.archive.org/web/20090319015937/http://www.rjamorim.com/rrw/files/astrid.zip";
	loc       = "wine";
	bin       = "c:\\dexvert\\astrid\\AACDEC.EXE";
	args      = async r => [r.inFile(), await r.outFile("out.wav")];
	renameOut = true;
	chain     = "sox[type:wav]";
}
