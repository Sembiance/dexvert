import {Program} from "../../Program.js";

export class plistutil extends Program
{
	website    = "https://www.libimobiledevice.org/";
	package    = "app-pda/libplist";
	bin        = "plistutil";
	args       = async r => ["-i", r.inFile(), "-o", await r.outFile("out.xml")];
	renameOut  = true;
}
