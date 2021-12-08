import {Program} from "../../Program.js";

export class gunzip extends Program
{
	website       = "https://www.gnu.org/software/gzip/";
	package       = "app-arch/gzip";
	bin           = "gunzip";
	args          = r => ["--force", r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	renameOut     = false;
}
