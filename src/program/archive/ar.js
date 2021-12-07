import {Program} from "../../Program.js";

export class ar extends Program
{
	website   = "https://sourceware.org/binutils/";
	package   = "sys-devel/binutils";
	bin       = "ar";
	args      = r => ["xo", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
