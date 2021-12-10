import {Program} from "../../Program.js";

export class zoo extends Program
{
	website   = "https://packages.debian.org/jessie/zoo";
	package   = "app-arch/zoo";
	bin       = "zoo";
	cwd       = r => r.outDir();
	args      = r => ["-extract", r.inFile()];
	renameOut = false;
}
