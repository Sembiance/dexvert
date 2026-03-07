import {Program} from "../../Program.js";
import {path} from "std";

export class arl2wav extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "python3";
	args       = r => [path.join(Program.binPath("arl2wav"), "arl2wav.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut  = false;
	skipVerify = true;
	chain      = "sox[type:wav][skipVerify]";
}
