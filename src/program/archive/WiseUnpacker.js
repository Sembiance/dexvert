import {xu} from "xu";
import {Program} from "../../Program.js";

export class WiseUnpacker extends Program
{
	website   = "https://github.com/mnadareski/WiseUnpacker";
	package   = "app-arch/WiseUnpacker";
	unsafe    = true;
	bin       = "WiseUnpacker";
	args      = r => ["--extract", `--outdir=${r.outDir()}`, r.inFile()];
	renameOut = true;
}
