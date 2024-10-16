import {Program} from "../../Program.js";

export class sapfs extends Program
{
	website   = "http://nostalgies.thomsonistes.org/transfert.html";
	package   = "app-arch/saptools";
	bin       = "sapfs";
	args      = r => ["--extract-all", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
