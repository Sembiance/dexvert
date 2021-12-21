import {xu} from "xu";
import {Program} from "../../Program.js";

export class dexvert extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags   = {
		asFormat : "Which format to convert as"
	};

	unsafe     = true;
	bin        = "/mnt/compendium/.deno/bin/dexvert";
	args       = r => [...(r.flags.asFormat ? [`--asFormat=${r.flags.asFormat}`] : []), `--logLevel=${r.xlog.level}`, "--", r.inFile(), r.outDir()];
	renameIn   = false;	// RunState.originalInput would be lost and dexvert should be able to handle any incoming filename
	renameOut  = false;
	runOptions = r => ({liveOutput : r.xlog.atLeast("trace")});
}
