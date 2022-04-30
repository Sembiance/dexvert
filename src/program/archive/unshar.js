import {Program} from "../../Program.js";

export class unshar extends Program
{
	website   = "https://www.gnu.org/software/sharutils/";
	package   = "app-arch/sharutils";
	bin       = "unshar";
	args      = r => ["--overwrite", "-d", r.outDir(), r.inFile()];
	renameOut = false;
}
