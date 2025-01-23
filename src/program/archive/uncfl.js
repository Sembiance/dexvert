import {Program} from "../../Program.js";

export class uncfl extends Program
{
	website   = "https://solhsa.com/cfl/";
	loc       = "wine";
	bin       = "uncfl.exe";
	args      = r => [r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
