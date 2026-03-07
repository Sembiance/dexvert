import {Program} from "../../Program.js";
import {path} from "std";

export class sbk2wav extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "python3";
	args       = r => [path.join(Program.binPath("sbk2wav"), "sbk2wav.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut  = false;
	skipVerify = true;
	chain      = "sox[type:wav][skipVerify]";
}
