import {Program} from "../../Program.js";
import {path} from "std";

export class esriShape2svg extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = "python3";
	args      = async r => [path.join(Program.binPath("esriShape2svg"), "esriShape2svg.py"), r.inFile(), await r.outFile("out.svg")];
	chain     = "deDynamicSVG";
	renameOut = true;
}
