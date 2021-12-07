import {Program} from "../../Program.js";

export class arc extends Program
{
	website   = "http://arc.sourceforge.net";
	package   = "app-arch/arc";
	unsafe    = true;
	bin       = "arc";
	args      = r => ["x", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
