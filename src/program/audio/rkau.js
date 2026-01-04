import {Program} from "../../Program.js";

export class rkau extends Program
{
	website   = "https://www.sac.sk/download/pack/rkau107.zip";
	loc       = "wine";
	bin       = "rkau107\\rkau.exe";
	args      = r => [r.inFile()];
	cwd       = r => r.outDir();
	renameOut = true;
	chain     = "sox[type:wav]";
}
