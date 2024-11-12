import {Program} from "../../Program.js";

export class abc2mid extends Program
{
	website   = "https://ifdo.ca/~seymour/runabc/top.html";
	package   = "media-sound/abcmidi";
	unsafe    = true;
	bin       = "abc2midi";
	args      = async r => [r.inFile(), "-o", await r.outFile("out.mid")];
	renameOut = true;
	chain     = "timidity";
}
