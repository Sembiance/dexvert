import {Program} from "../../Program.js";

export class gamearch extends Program
{
	website      = "https://github.com/Malvineous/libgamearchive";
	package      = "dev-libs/libgamearchive";
	bin          = "gamearch";
	args         = r => ["-X", r.inFile()];
	cwd          = r => r.outDir();
	checkForDups = true;
	failOnDups   = true;
	renameOut    = false;
	notes        = "A newer 100% NodeJS version available here: https://github.com/camoto-project/gamearchivejs";
}
