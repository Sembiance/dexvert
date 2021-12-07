import {Program} from "../../Program.js";

export class dumpamos extends Program
{
	website   = "https://github.com/kyz/amostools/";
	package   = "dev-lang/amostools";
	bin       = "dumpamos";
	cwd       = r => r.outDir();
	args      = r => [r.inFile()];
	renameOut = false;
}
