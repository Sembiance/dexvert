import {xu} from "xu";
import {Program} from "../../Program.js";

export class dexvert extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags =
	{
		asFormat : "Which format to convert as"
	};

	unsafe     = true;
	bin        = "/mnt/compendium/.deno/bin/dexvert";
	args       = r => [...(r.flags.asFormat ? [`--asFormat=${r.flags.asFormat}`] : []), `--verbose=${xu.verbose<4 ? 0 : xu.verbose}`, r.inFile(), r.outDir()]
	runOptions = ({liveOutput : true});
}
