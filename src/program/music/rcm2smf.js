import {Program} from "../../Program.js";

export class rcm2smf extends Program
{
	website   = "https://github.com/shingo45endo/rcm2smf";
	package   = "media-sound/mus2mid";
	unsafe    = true;
	bin       = "node";
	args      = async r => [Program.binPath("rcm2smf/rcm2smf.js"), r.inFile(), await r.outFile("out.smf")];
	renameOut = true;
	chain     = "timidity";
}
