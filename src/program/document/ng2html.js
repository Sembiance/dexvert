import {Program} from "../../Program.js";

export class ng2html extends Program
{
	website    = "http://www.davep.org/norton-guides/";
	package    = "app-text/ng2html";
	unsafe     = true;
	bin        = "ng2html";
	args       = r => [r.inFile()];
	cwd        = r => r.outDir();
	skipVerify = true;
	renameOut  = false;
}
