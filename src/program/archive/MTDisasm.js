import {xu} from "xu";
import {Program} from "../../Program.js";

export class MTDisasm extends Program
{
	website   = "https://github.com/elasota/MTDisasm";
	package   = "app-arch/MTDisasm";
	bin       = "unbundle";
	args      = r => ["assets", r.inFile(), r.outDir()];
	renameOut = false;
}
