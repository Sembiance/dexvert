import {xu} from "xu";
import {Program} from "../../Program.js";

export class qtflatt extends Program
{
	flags = {
		chainAs : "Chain as a particular format"
	};
	checkForDups = true;
	bin          = "python3";
	args         = async r => [Program.binPath("qtflatt.py"), r.inFile(), await r.outFile("out.mov")];
	chain        = r => (r.flags.chainAs?.length ? `dexvert[asFormat:${r.flags.chainAs}]` : "dexvert");
	renameOut    = true;
}
