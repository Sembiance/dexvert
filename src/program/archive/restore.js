import {xu} from "xu";
import {Program} from "../../Program.js";

export class restore extends Program
{
	website   = "https://dump.sourceforge.io/";
	package   = "app-arch/dump";
	unsafe    = true;
	bin       = "restore";
	args      = r => ["-r", "-y", "-f", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
