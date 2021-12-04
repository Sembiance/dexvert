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
	args       = r => [...(r.flags.asFormat ? [`--asFormat=${r.flags.asFormat}`] : []), `--logLevel=${r.xlog.atLeast("debug") ? r.xlog.level : "none"}`, r.inFile(), r.outDir()];
	runOptions = ({liveOutput : true});
}
