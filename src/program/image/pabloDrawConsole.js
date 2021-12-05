import {xu} from "xu";
import {Program} from "../../Program.js";

export class pabloDrawConsole extends Program
{
	website    = "http://picoe.ca/products/pablodraw/";
	package    = "media-gfx/pablodraw-console";
	unsafe     = true;
	bin        = "pablodraw-console";
	args       = async r => [`--convert=${r.inFile()}`, `--out=${await r.outFile("out.png")}`];
	runOptions = {timeout : xu.MINUTE*2};	// This can hang at 100% on some files like GRIMMY2.RIP
}
