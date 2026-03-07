import {Program} from "../../Program.js";
import {path} from "std";

export class elecmugen2wav extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("elecmugen2wav"), "elecmugen2wav.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
	chain     = "sox[type:wav]";
}
