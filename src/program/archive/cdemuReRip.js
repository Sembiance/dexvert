import {xu} from "xu";
import {Program} from "../../Program.js";

export class cdemuReRip extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	package    = ["app-cdr/cdemu", "app-cdr/cdrdao"];
	bin        = "deno";
	unsafe     = true;
	args       = r => Program.denoArgs(Program.binPath("cdemuReRip.js"), r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	renameOut  = false;
}
