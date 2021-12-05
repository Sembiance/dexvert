import {Program} from "../../Program.js";

export class unadf extends Program
{
	website   = "http://lclevy.free.fr/adflib/";
	package   = "app-arch/unadf";
	bin       = "unadf";
	args      = r => [r.inFile(), "-d", r.outDir()];
	renameOut = false;
}
