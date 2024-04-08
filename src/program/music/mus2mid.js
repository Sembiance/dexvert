import {Program} from "../../Program.js";

export class mus2mid extends Program
{
	website   = "https://github.com/Sembiance/mus2mid";
	package   = "media-sound/mus2mid";
	unsafe    = true;
	bin       = "mus2mid";
	args      = async r => [r.inFile(), await r.outFile("out.mid")];
	renameOut = true;
	chain     = "timidity";
}
