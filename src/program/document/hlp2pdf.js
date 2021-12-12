import {xu} from "xu";
import {Program} from "../../Program.js";

export class hlp2pdf extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = Program.binPath("hlp2rtf/hlp2rtf.js");
	args      = async r => ["--", r.inFile(), await r.outFile("out.rtf")];
	chain     = "dexvert[asFormat:document/rtf]";
	renameOut = true;
}
