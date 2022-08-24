import {Program} from "../../Program.js";

export class freeze extends Program
{
	website       = "http://fileformats.archiveteam.org/wiki/Freeze/Melt";
	package       = "app-arch/freeze";
	bin           = "freeze";
	args          = r => ["-d", r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	renameOut     = false;
}
