import {xu} from "xu";
import {Program} from "../../Program.js";

export class uncmz extends Program
{
	website   = "https://github.com/sourcekris/uncmz";
	package   = "app-arch/uncmz";
	bin       = "uncmz";
	args      = r => ["-d", r.outDir(), "-e", r.inFile()];
	renameOut = false;
}
