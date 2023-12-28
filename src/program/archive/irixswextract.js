import {xu} from "xu";
import {Program} from "../../Program.js";

export class irixswextract extends Program
{
	website   = "https://github.com/Sembiance/irixswextract";
	package   = "app-arch/irixswextract";
	bin       = "irixswextract";
	args      = r => [".", r.inFile(), r.outDir()];
	renameOut = false;
}
