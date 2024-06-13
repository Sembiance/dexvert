import {xu} from "xu";
import {Program} from "../../Program.js";

export class applesoftBASIC2txt extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	unsafe     = true;
	args       = async r => Program.denoArgs(Program.binPath("applesoftBASIC2txt.js"), "--", r.inFile(), await r.outFile("out.txt"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
}
