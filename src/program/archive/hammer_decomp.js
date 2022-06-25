import {Program} from "../../Program.js";
import {path} from "std";

export class hammer_decomp extends Program
{
	website   = "https://github.com/Treeki/RandomStuff/blob/master/hammer_decomp.py";
	bin       = "python";
	args      = async r => [path.join(Program.binPath("hammer_decomp"), "hammer_decomp.py"), r.inFile(), await r.outFile("outfile")];
	renameOut = true;
}
