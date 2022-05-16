import {Program} from "../../Program.js";

export class atr extends Program
{
	website   = "https://github.com/jhallen/atari-tools";
	package   = "app-arch/atari-tools";
	bin       = "atr";
	unsafe    = true;
	args      = r => [r.inFile(), "x", "-a"];
	cwd       = r => r.outDir();
	renameOut = false;
}
