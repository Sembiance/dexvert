import {Program} from "../../Program.js";
import {path} from "std";

export class undpk extends Program
{
	website   = "http://fileformats.archiveteam.org/wiki/DPK";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("undpk"), "undpk.py"), r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
