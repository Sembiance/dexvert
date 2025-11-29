import {Program} from "../../Program.js";

export class jvcextract extends Program
{
	website   = "https://github.com/mseminatore/dsktools";
	package   = "app-arch/jvcextract";
	bin       = "jvcextract";
	args      = r => [r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
