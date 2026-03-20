import {Program} from "../../Program.js";

export class texture2d2png extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	unsafe    = true;
	args      = async r => [Program.binPath("texture2d2png.py"), r.inFile({absolute : true}), await r.outFile("out.png", {absolute : true})];
	renameOut = true;
}
