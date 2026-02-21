import {Program} from "../../Program.js";

export class emf2svg extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [Program.binPath("emf2svg.py"), r.inFile({absolute : true}), await r.outFile("out.svg", {absolute : true})];
	chain     = "deDynamicSVG[autoCrop]";
	renameOut = true;
}
