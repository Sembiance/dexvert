import {Program} from "../../Program.js";

export class msa extends Program
{
	website       = "https://web.archive.org/web/20060507110406/https://www.uni-ulm.de/~s_thuth/ix/msa-0.1.0.tar.gz";
	package       = "app-arch/msa";
	bin           = "msa";
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = true;
	chain         = "uniso[checkMount]";
}
