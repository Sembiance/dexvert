import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2svg extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	bin     = "python3";
	args    = async r => [path.join(Program.binPath("vibe2svg"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), await r.outFile("out.svg")];
	flags   = {
		autoCrop : "Auto crop the SVG output"
	};
	chain     = r => (r.flags.autoCrop ? "deDynamicSVG[autoCrop]" : "deDynamicSVG");
	renameOut = true;
}
