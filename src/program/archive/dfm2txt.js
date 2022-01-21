import {Program} from "../../Program.js";

export class dfm2txt extends Program
{
	website = "http://github.com/Sembiance/dexvert";
	flags   = {
		type : `Which type of input file, bin or res. Default: bin`
	};
	loc       = "win2k";
	bin       = "dfm2txt.exe";
	args      = r => [r.flags.type || "bin", r.inFile(), "c:\\out\\out.txt"];
	renameOut = true;
	chain     = "undfm";
}
