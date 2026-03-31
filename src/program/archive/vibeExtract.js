import {Program} from "../../Program.js";
import {path} from "std";

export class vibeExtract extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("vibeExtract"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), r.outDir()];
	renameOut = false;
}
