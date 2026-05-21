import {Program} from "../../Program.js";
import {path} from "std";

export class vibeExtract extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	bin     = "python3";
	flags   = {
		singleFile : "Extractor just converts to a single file"
	};
	args      = async r => [path.join(Program.binPath("vibeExtract"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), r.flags.singleFile ? await r.outFile("out.ans") : r.outDir()];
	renameOut = false;
}
