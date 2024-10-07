import {xu} from "xu";
import {Program} from "../../Program.js";

export class unFrontPageThemePack extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("unFrontPageThemePack.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	renameOut  = false;
}
