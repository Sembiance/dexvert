import {xu} from "xu";
import {Program} from "../../Program.js";

export class cadius extends Program
{
	website   = "https://github.com/mach-kernel/cadius";
	package   = "app-arch/cadius";
	bin       = "cadius";
	args      = r => ["EXTRACTVOLUME", r.inFile(), r.outDir()];
	renameOut = false;
}
