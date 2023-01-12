import {Program} from "../../Program.js";

export class innounp extends Program
{
	website   = "https://innounp.sourceforge.net/";
	loc       = "win2k";
	bin       = "c:\\dexvert\\innounp.exe";
	args      = r => ["-x", "-b", "-q", "-m", "-dc:\\out", "-a", "-y", r.inFile()];
	renameOut = false;
}
