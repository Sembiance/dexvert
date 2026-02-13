import {Program} from "../../Program.js";
import {path} from "std";

export class pdn2png extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	unsafe    = true;
	args      = async r => [path.join(Program.binPath("pdn2png"), "pdn2png.py"), r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
