import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2pdf extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [path.join(Program.binPath("vibe2pdf"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), await r.outFile("out.pdf")];
	renameOut = true;
}
