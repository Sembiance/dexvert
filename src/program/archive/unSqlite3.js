import {xu} from "xu";
import {Program} from "../../Program.js";

export class unSqlite3 extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = Program.binPath("unSqlite3.sh");
	args      = r => [r.inFile(), r.outDir()];
	renameOut = false;
}
