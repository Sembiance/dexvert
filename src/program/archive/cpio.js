import {Program} from "../../Program.js";

export class cpio extends Program
{
	website   = "https://www.gnu.org/software/cpio/cpio.html";
	package   = "app-arch/cpio";
	bin       = "cpio";
	args      = r => ["--extract", `--file=${r.inFile()}`, `--directory=${r.outDir()}`];
	renameOut = false;
}
