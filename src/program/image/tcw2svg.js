import {Program} from "../../Program.js";

export class tcw2svg extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = "python3";
	args      = async r => [Program.binPath("tcw2svg.py"), r.inFile(), await r.outFile("out.svg")];
	chain     = "deDynamicSVG";
	renameOut = true;
}
