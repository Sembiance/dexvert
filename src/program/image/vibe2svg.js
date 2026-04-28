import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2svg extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	bin     = "python3";
	flags   = {
		multiple : "Converter will produce multiple SVG files instead of just 1",
		autoCrop : "Auto crop the SVG output"
	};
	args      = async r => [path.join(Program.binPath("vibe2svg"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), r.flags.multiple ? r.outDir() : await r.outFile("out.svg")];
	chain     = r => (r.flags.autoCrop ? "deDynamicSVG[autoCrop]" : "deDynamicSVG");
	renameOut = r => !r.flags.multiple;
}
