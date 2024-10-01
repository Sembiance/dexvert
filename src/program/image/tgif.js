import {Program} from "../../Program.js";

export class tgif extends Program
{
	website       = "http://bourbon.usc.edu/tgif/index.html";
	package       = "media-gfx/tgif";
	bin           = "tgif";
	args          = r => ["-print", "-ps", r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	renameOut     = true;
	chain         = "ps2pdf[svg]";
}
