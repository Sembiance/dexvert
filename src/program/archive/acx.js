import {xu} from "xu";
import {Program} from "../../Program.js";

export class acx extends Program
{
	website   = "https://github.com/AppleCommander/AppleCommander";
	package   = "app-arch/AppleCommander";
	bin       = "acx";
	args      = r => ["x", "--suggested", "-d", r.inFile(), "-o", r.outDir()];
	renameOut = false;
	chain     = "unHexACX";
}
