import {Program} from "../../Program.js";

export class iat extends Program
{
	website    = "https://www.berlios.de/software/iso9660-analyzer-tool/";
	package    = "app-cdr/iat";
	bin        = "iat";
	args       = r => ["-i", r.inFile(), "--cue", "-o", "out"];
	cwd        = r => r.outDir();
	renameOut  = false;
	chain      = "?dexvert";
	chainCheck = (r, chainFile) => [".bin"].includes(chainFile.ext.toLowerCase());
}
