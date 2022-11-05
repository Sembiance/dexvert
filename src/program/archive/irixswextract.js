import {xu} from "xu";
import {Program} from "../../Program.js";

export class irixswextract extends Program
{
	website   = "https://gist.github.com/Sgeo/ff7c568e81b7efa09250dc3fc1253569";
	bin       = Program.binPath("irixswextract/irixswextract");
	args      = r => [".", r.inFile(), r.outDir()];
	renameOut = false;
}
