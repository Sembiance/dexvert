import {xu} from "xu";
import {Program} from "../../Program.js";

export class endoom2ans extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = async r => Program.denoArgs(Program.binPath("endoom2ans.js"), r.inFile(), await r.outFile("out.ans"));
	runOptions = ({env : Program.denoEnv()});
	unsafe     = true;
	renameOut  = true;
	chain      = "deark[module:ansiart][charOutType:image]";
}
