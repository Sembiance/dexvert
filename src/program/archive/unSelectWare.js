import {Program} from "../../Program.js";

export class unSelectWare extends Program
{
	website   = "https://moddingwiki.shikadi.net/wiki/SelectWare_Archive";
	package   = "app-arch/unSelectWare";
	bin       = "unSelectWare";
	args      = r => [r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
