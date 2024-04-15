import {xu} from "xu";
import {Program} from "../../Program.js";

export class steve2wav extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = async r => Program.denoArgs(Program.binPath("steve2wav.js"), "--", r.inFile(), await r.outFile("out.wav"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
	chain      = "sox";
}
