import {xu} from "xu";
import {Program} from "../../Program.js";

export class unp64 extends Program
{
	website       = "https://iancoog.altervista.org/";
	package       = "app-arch/unp64";
	bin           = "unp64";
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = true;
}
