import {xu} from "xu";
import {Program} from "../../Program.js";

export class exeUnPostContent extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	flags   = {
		idstring : "Which idstring must match to extract the appended content",
		ext      : "Output file extension"
	};
	args       = async r => Program.denoArgs(Program.binPath("exeUnPostContent.js"), r.flags.idstring, r.inFile(), await r.outFile(`out${r.flags.ext}`));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
}
