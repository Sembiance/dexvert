import {Program} from "../../Program.js";

export class xar extends Program
{
	website   = "https://github.com/apple-oss-distributions/xar";
	package   = "app-arch/xar";
	bin       = "xar";
	args      = r => ["-xf", r.inFile(), "-C", r.outDir()];
	renameOut = false;
}
