import {xu} from "xu";
import {Program} from "../../Program.js";

export class lmp2ppm extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = async r => Program.denoArgs(Program.binPath("lmp2ppm.js"), `--palette=${r.f.aux.base}`, r.inFile(), await r.outFile("out.ppm"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
	chain      = "convert";
}
