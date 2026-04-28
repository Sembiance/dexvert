import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2mid extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [path.join(Program.binPath("vibe2mid"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), await r.outFile("out.mid")];
	renameOut = true;
	chain     = "timidity";
}
