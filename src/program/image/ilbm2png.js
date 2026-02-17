import {Program} from "../../Program.js";

export class ilbm2png extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [Program.binPath("ilbm2png.py"), r.inFile({absolute : true}), await r.outFile("out.png", {absolute : true})];
	renameOut = true;
}
