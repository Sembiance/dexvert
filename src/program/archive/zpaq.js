import {Program} from "../../Program.js";

export class zpaq extends Program
{
	website   = "http://mattmahoney.net/dc/zpaq.html";
	package   = "app-arch/zpaq";
	bin       = "zpaq";
	args      = r => ["x", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
