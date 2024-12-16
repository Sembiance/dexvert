import {xu} from "xu";
import {Program} from "../../Program.js";

export class unHLPMVB extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	package = ["app-arch/helpdeco", "media-libs/resvg"];
	flags   = {
		extractExtra : "Set to true to also extract any other non-referenced embedded files"
	};
	bin        = "deno";
	unsafe     = true;
	args       = r => Program.denoArgs(Program.binPath("unHLPMVB.js"), ...(r.flags.extractExtra ? ["--extractExtra"] : []), `--outFilename=${r.originalInput ? r.originalInput.name : "out"}`, "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	skipVerify = true;	// some files are HUGE, this one produces 16,172 files: https://dev.discmaster2.textfiles.com/browse/18393/CMGE-2001-CD2.iso/Media.m14
	renameOut  = false;
	chain      = "?dexvert[asFormat:document/rtf]";
	chainCheck = (r, chainFile) => [".rtf"].includes(chainFile.ext.toLowerCase());
}
