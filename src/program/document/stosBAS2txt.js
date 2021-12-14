import {xu} from "xu";
import {Program} from "../../Program.js";

export class stosBAS2txt extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = async r => Program.denoArgs(Program.binPath("stosBAS2txt.js"), "--", r.inFile(), await r.outFile("out.txt"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
}
