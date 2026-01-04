import {xu} from "xu";
import {Program} from "../../Program.js";

export class fssd2wav extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("fssd2wav.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
	chain      = "sox[type:wav]";
}
