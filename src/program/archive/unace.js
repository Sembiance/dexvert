import {Program} from "../../Program.js";

export class unace extends Program
{
	website       = "http://www.winace.com/";
	package       = "app-arch/unace";
	bin           = "unace";
	args          = r => ["x", "-y", r.inFile()];
	cwd           = r => r.outDir();
	renameOut     = false;
}
