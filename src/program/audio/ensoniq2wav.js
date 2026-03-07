import {Program} from "../../Program.js";
import {path} from "std";

export class ensoniq2wav extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "python3";
	args       = r => [path.join(Program.binPath("ensoniq2wav"), "ensoniq2wav.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut  = false;
	skipVerify = true;
	chain      = "sox[type:wav][skipVerify]";
}
