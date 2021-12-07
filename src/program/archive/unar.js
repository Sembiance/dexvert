import {Program} from "../../Program.js";

export class unar extends Program
{
	website   = "https://unarchiver.c3.cx/";
	package   = "app-arch/unar";
	bin       = "unar";
	args      = r => ["-f", "-D", "-o", r.outDir(), r.inFile()];
	renameOut = false;
}
