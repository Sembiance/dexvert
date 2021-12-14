import {Program} from "../../Program.js";

export class texi2html extends Program
{
	website   = "http://www.nongnu.org/texi2html/";
	package   = "app-text/texi2html";
	unsafe    = true;
	bin       = "texi2html";
	cwd       = r => r.outDir();
	args      = r => ["--l2h-tmp", r.f.root, "--l2h-clean", r.inFile()];
	renameOut = true;
}
