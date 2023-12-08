import {Program} from "../../Program.js";

export class devoc extends Program
{
	website       = "https://www.dechifro.org/rca/";
	bin           = Program.binPath("devoc/devoc");
	args          = r => ["-w", r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = true;
	chain         = "sox";
}
