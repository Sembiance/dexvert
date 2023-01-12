import {Program} from "../../Program.js";

export class bunzip2 extends Program
{
	website       = "https://gitlab.com/federicomenaquintero/bzip2";
	package       = "app-arch/bzip2";
	bin           = "bunzip2";
	args          = r => ["--force", r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	checkForDups  = true;
	renameOut     = false;
}
