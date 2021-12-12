import {Program} from "../../Program.js";

export class WoW extends Program
{
	website = "http://aminet.net/package/util/conv/WoW";
	loc     = "amigappc";
	bin     = "WoW";
	args    = r => ["-asc", r.inFile(), "HD:out/outfile.txt"];
	
	// When WoW fails, it produces files with a single newline in it, so we filter those out here
	verify    = (r, dexFile) => dexFile.size>1;
	renameOut = true;
}
