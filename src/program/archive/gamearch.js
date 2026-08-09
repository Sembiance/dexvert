import {Program} from "../../Program.js";

export class gamearch extends Program
{
	website      = "https://github.com/Malvineous/libgamearchive";
	package      = "dev-libs/libgamearchive";
	flags   = {
		format : "Specify which format to convert as. Default: let gamearch decide"	// for list run: gamearch --list-types
	};
	bin          = "gamearch";
	args         = r => [...(r.flags.format ? ["--type", r.flags.format] : []), "-X", r.inFile()];
	cwd          = r => r.outDir();
	checkForDups = true;
	failOnDups   = true;
	renameOut    = false;
	notes        = "A newer 100% NodeJS version available here: https://github.com/camoto-project/gamearchivejs";
}
