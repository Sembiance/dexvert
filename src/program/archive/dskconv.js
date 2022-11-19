import {Program} from "../../Program.js";

export class dskconv extends Program
{
	website      = "http://www.seasip.info/Unix/LibDsk/";
	package      = "app-emulation/libdsk";
	checkForDups = true;
	unsafe       = true;
	bin          = "dskconv";
	args         = async r => [r.inFile(), "-otype", "raw", await r.outFile("out")];
	renameOut    = true;
}
