import {xu} from "xu";
import {Program} from "../../Program.js";

export class ppmz extends Program
{
	website   = "http://www.cs.hut.fi/u/tarhio/ppmz/";
	bin       = Program.binPath("ppmz");
	args      = async r => [r.inFile(), await r.outFile("outfile")];
	renameOut = true;
}
