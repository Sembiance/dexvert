import {xu} from "xu";
import {Program} from "../../Program.js";

export class fix7zCUR extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	flags = {
		outputFilePath : "Relative path for output"
	};
	args       = async r => Program.denoArgs(Program.binPath("fix7zCUR.js"), "--", r.inFile(), r.flags.outputFilePath || await r.outFile("out.cur"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
}
