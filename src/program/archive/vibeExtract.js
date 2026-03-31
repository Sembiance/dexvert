import {Program} from "../../Program.js";
import {path} from "std";

export class vibeExtract extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags   = {
		format : "Format to extract, required"
	};
	bin       = "python3";
	args      = r => [path.join(Program.binPath("vibeExtract"), r.flags.format, `${r.flags.format}.py`), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
