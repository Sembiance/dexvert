import {Program} from "../../Program.js";
import {path} from "std";

export class cpt2png extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	unsafe    = true;
	args      = async r => [path.join(Program.binPath("cpt2png"), "cpt2png.py"), r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
