import {xu} from "xu";
import {Program} from "../../Program.js";

export class unp64 extends Program
{
	website        = "https://iancoog.altervista.org/";
	package        = "app-arch/unp64";
	bin            = "unp64";
	args           = r => [r.inFile()];
	cwd            = r => r.outDir();
	mirrorInToCWD  = true;
	checkForDups   = true;
	unsafe         = true;
	//forbidChildRun = true;	// infinite loop with: archive/packedC64PRG/happy birthday		(worked around it in that format by excluding a packer format)
	renameOut      = true;
}
