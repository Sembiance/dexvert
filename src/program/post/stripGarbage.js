import {xu} from "xu";
import {Program} from "../../Program.js";

export class stripGarbage extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	flags   = {
		"null"  : "Only strip null bytes",
		"ascii" : "Only strip if the remainder of the file is ASCII"
	};
	bin       = Program.binPath("stripGarbage/stripGarbage");
	args      = async r => [...(r.flags.null ? ["--null"] : []), ...(r.flags.ascii ? ["--ascii"] : []), r.inFile(), await r.outFile("out.txt")];
	renameOut = true;
}
