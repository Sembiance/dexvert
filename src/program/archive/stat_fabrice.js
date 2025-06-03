import {Program} from "../../Program.js";

export class stat_fabrice extends Program
{
	website       = "https://bellard.org/stat/";
	package       = "app-arch/stat_fabrice";
	bin           = "stat_fabrice";
	args          = r => ["-n", "-d", r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = true;
}
