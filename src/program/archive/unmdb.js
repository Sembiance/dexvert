import {xu} from "xu";
import {Program} from "../../Program.js";

export class unmdb extends Program
{
	website    = "https://github.com/mdbtools/mdbtools";
	package    = "app-office/mdbtools";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("unmdb.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
}
