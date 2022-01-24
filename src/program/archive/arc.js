import {xu} from "xu";
import {Program} from "../../Program.js";

export class arc extends Program
{
	website    = "http://arc.sourceforge.net";
	package    = "app-arch/arc";
	unsafe     = true;
	bin        = "arc";
	args       = r => ["xo", r.inFile()];
	cwd        = r => r.outDir();
	renameOut  = false;
	verify     = r => !r.stdout.includes("fails CRC check");
}
