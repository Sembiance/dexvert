import {xu} from "xu";
import {Program} from "../../Program.js";

export class pvr2png extends Program
{
	website   = "https://fabiensanglard.net/Mykaruga/";
	bin       = "pvr2png.exe";
	args      = r => [r.inFile(), "c:\\out\\out.png"];
	loc       = "win2k";
	renameOut = true;
}
