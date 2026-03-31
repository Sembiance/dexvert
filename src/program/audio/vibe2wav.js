import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2wav extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "python3";
	args       = r => [path.join(Program.binPath("vibe2wav"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), r.outDir()];
	renameOut  = false;
	skipVerify = true;
	chain      = "sox[type:wav][skipVerify]";
}
