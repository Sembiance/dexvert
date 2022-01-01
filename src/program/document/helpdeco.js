import {Program} from "../../Program.js";

export class helpdeco extends Program
{
	website   = "https://sourceforge.net/projects/helpdeco/";
	package   = "app-arch/helpdeco";
	bin       = "helpdeco";
	args      = r => ["-y", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
	notes     = "This will just EXTRACT the files. For proper HLP conversion, run hlp2pdf instead";
}
