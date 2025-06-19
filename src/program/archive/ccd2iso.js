import {Program} from "../../Program.js";

export class ccd2iso extends Program
{
	website   = "https://sourceforge.net/projects/ccd2iso/";
	package   = "app-cdr/ccd2iso";
	bin       = "ccd2iso";
	args      = async r => [r.inFile(), await r.outFile("out.iso")];
	chain     = "dexvert[skipVerify][bulkCopyOut]";
	renameOut = true;
}
