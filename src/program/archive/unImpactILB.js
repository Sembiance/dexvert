import {Program} from "../../Program.js";

export class unImpactILB extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("unImpactILB.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	renameOut = false;
}
