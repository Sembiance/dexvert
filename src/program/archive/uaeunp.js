import {xu} from "xu";
import {Program} from "../../Program.js";

export class uaeunp extends Program
{
	website      = "https://www.winuae.net/download/";
	loc          = "wine";
	bin          = "uaeunp.exe";
	args         = r => ["-x", r.inFile(), "**"];
	wineData  = {
		timeout : xu.MINUTE*2
	};
	cwd          = r => r.outDir();
	checkForDups = true;
	renameOut    = false;
}
