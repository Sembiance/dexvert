import {xu} from "xu";
import {Program} from "../../Program.js";

export class wimapply extends Program
{
	website   = "https://wimlib.net";
	package   = "app-arch/wimlib";
	bin       = "wimapply";
	args      = r => [r.inFile(), r.outDir()];
	renameOut = false;
}
