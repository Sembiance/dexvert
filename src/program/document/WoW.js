import {Program} from "../../Program.js";

export class WoW extends Program
{
	website = "http://aminet.net/package/util/conv/WoW";
	loc     = "amiga";
	unsafe  = true;
	bin     = "WoW";
	args    = r => ["-asc", r.inFile(), "HD:out/outfile.txt"];
	
	// When WoW fails, it produces files with just a few newlines in it, so we filter those out here with a reasonable size check
	verify    = (r, dexFile) => dexFile.size>=32;
	renameOut = true;
}
