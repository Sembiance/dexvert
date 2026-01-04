import {xu} from "xu";
import {Program} from "../../Program.js";

export class exe2bik extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = async r => Program.denoArgs(Program.binPath("exe2bik.js"), r.inFile(), await r.outFile("out.bik"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
}
