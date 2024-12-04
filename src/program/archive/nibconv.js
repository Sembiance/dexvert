import {Program} from "../../Program.js";

export class nibconv extends Program
{
	website   = "https://github.com/rittwage/nibtools";
	loc       = "wine";
	bin       = "c:\\dexvert\\nibtools\\nibconv.exe";
	args      = async r => [r.inFile(), await r.outFile("out.g64")];
	renameOut = true;
	chain     = "dexvert[asFormat:archive/commodoreDiskImage]";
	notes     = "Has a linux version, but requires OpenCBM to be installed to compiled to which is some kernel level driver crap so meh, just use the win32 version with wine";
}
