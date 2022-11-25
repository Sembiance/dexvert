import {Program} from "../../Program.js";

export class unautoCADSlideLibrary extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	package    = "media-libs/netpbm";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("unautoCADSlideLibrary.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	renameOut  = false;
	chain      = "convert";
}
