import {xu} from "xu";
import {Program} from "../../Program.js";

export class unHLPMVB extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	unsafe     = true;
	args       = r => Program.denoArgs(Program.binPath("unHLPMVB.js"), `--outFilename=${r.originalInput ? r.originalInput.name : "out"}`, "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	renameOut  = false;
	chain      = "?dexvert[asFormat:document/rtf]";
	chainCheck = (r, chainFile) => [".rtf"].includes(chainFile.ext.toLowerCase());
}
