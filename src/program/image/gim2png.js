import {Program} from "../../Program.js";

export class gim2png extends Program
{
	website       = "https://www.junk2ool.net/_media/tools/psx/gim2png01.7z";
	loc           = "wine";
	bin           = "c:\\dexvert\\GIM2PNG.EXE";
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = true;
}
