import {Program} from "../../Program.js";

export class uudecode extends Program
{
	website   = "https://www.gnu.org/software/sharutils/";
	package   = "app-arch/sharutils";
	bin       = "uudecode";
	args      = r => [r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
