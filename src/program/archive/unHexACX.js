import {xu} from "xu";
import {Program} from "../../Program.js";

export class unHexACX extends Program
{
	website        = "https://github.com/Sembiance/dexvert";
	bin            = "deno";
	args           = r => Program.denoArgs(Program.binPath("unHexACX.js"), "--", r.inFile(), r.outDir());
	unsafe         = true;
	skipSafeRename = true;	// See sample/archive/appleDOSDiskImage/PRO.BYTER  (the ^ filename)
	runOptions     = ({env : Program.denoEnv()});
	allowDupOut    = true;
	renameOut      = false;
}
