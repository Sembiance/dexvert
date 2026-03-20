import {Program} from "../../Program.js";
import {path} from "std";

export class unred extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unred"), "unred.py"), r.inFile(), r.outDir()];
	renameOut = false;
}
