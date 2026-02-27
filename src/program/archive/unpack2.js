import {Program} from "../../Program.js";

export class unpack2 extends Program
{
	website       = "https://github.com/Sembiance/dexvert";
	bin           = Program.binPath("unpack2");
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = false;
}
