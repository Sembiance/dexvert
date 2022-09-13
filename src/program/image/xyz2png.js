import {Program} from "../../Program.js";

export class xyz2png extends Program
{
	website   = "https://github.com/EasyRPG/Tools";
	package   = "games-util/EasyRPG-Tools";
	bin       = "xyz2png";
	args      = r => [r.inFile()];
	cwd       = r => r.outDir();
	renameOut = true;
}
