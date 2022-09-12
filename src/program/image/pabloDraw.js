import {xu} from "xu";
import {Program} from "../../Program.js";

export class pabloDraw extends Program
{
	website    = "http://picoe.ca/products/pablodraw/";
	package    = "media-gfx/pablodraw";
	unsafe     = true;
	bin        = "PabloDraw";
	args       = async r => [`--convert=${r.inFile({absolute : true})}`, `--out=${await r.outFile("out.png", {absolute : true})}`];
	runOptions = {timeout : xu.MINUTE, timeoutSignal : "SIGKILL"};	// This can hang at 100% on some files like GRIMMY2.RIP see: https://github.com/cwensley/pablodraw/issues/43
	renameOut  = true;
}
