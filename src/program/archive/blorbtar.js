import {Program} from "../../Program.js";

export class blorbtar extends Program
{
	website   = "https://www.ifarchive.org/if-archive/programming/blorb/blorbtar-0.1.pl";
	bin       = "perl";
	args      = r => [Program.binPath("blorbtar-0.1.pl"), "x", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
