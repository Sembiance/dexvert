import {Program} from "../../Program.js";

export class lrzip extends Program
{
	website   = "https://github.com/ckolivas/lrzip";
	package   = "app-arch/lrzip";
	bin       = "lrzip";
	args      = r => ["-d", "-O", r.outDir(), r.inFile()];
	renameOut = true;
}
