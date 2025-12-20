import {xu} from "xu";
import {Program} from "../../Program.js";

export class unISV3 extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("unISV3.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	//chain      = "dexvert[asFormat:archive/installShieldZ]";	// We do NOT chain, as that would combine all output files into a single dir which could overwrite files
	renameOut  = false;
}
