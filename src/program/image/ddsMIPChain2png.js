import {Program} from "../../Program.js";

export class ddsMIPChain2png extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	unsafe    = true;
	args      = async r => [Program.binPath("ddsMIPChain2png.py"), r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
