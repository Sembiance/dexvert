import {xu} from "xu";
import {Program} from "../../Program.js";

export class jingTaoPic2jpg extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = async r => Program.denoArgs(Program.binPath("jingTaoPic2jpg.js"), r.inFile(), await r.outFile("out.jpg"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
}
