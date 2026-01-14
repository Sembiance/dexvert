import {Program} from "../../Program.js";

export class unasd extends Program
{
	website   = "https://www.sac.sk/download/pack/asd020.exe";
	loc       = "wine";
	bin       = "unasd.exe";
	args      = r => ["x", "-y", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
