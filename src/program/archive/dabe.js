import {xu} from "xu";
import {Program} from "../../Program.js";

export class dabe extends Program
{
	website    = "https://www.templetons.com/brad/";
	package    = "app-arch/abe";
	bin        = "dabe";
	args       = r => ["+i", r.inFile()];
	cwd        = r => r.outDir();
	renameOut  = false;
}
