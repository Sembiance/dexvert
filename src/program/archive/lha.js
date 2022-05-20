import {Program} from "../../Program.js";

export class lha extends Program
{
	website   = "https://github.com/jca02266/lha";
	package   = "app-arch/lha";
	bin       = "lha";
	args      = r => ["-x", "--system-kanji-code=utf8", `-w=${r.outDir()}`, r.inFile()];
	renameOut = false;
}
