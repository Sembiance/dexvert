import {xu} from "xu";
import {Program} from "../../Program.js";

export class defactory extends Program
{
	website   = "https://codeberg.org/CYBERDEV/defactory";
	package   = "app-arch/defactory";
	unsafe    = true;
	bin       = "defactory";
	args      = r => ["--extract", r.outDir(), r.inFile()];
	renameOut = true;
}
