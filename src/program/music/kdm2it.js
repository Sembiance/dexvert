import {Program} from "../../Program.js";

export class kdm2it extends Program
{
	website   = "http://advsys.net/ken/download.htm";
	package   = "media-sound/kdm2it";
	bin       = "kdm2it";
	args      = async r => [r.inFile(), await r.outFile("out.it")];
	renameOut = true;
	chain     = "dexvert[asFormat:music/impulseTracker]";
}
