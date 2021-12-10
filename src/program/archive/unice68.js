import {Program} from "../../Program.js";

export class unice68 extends Program
{
	website   = "http://sc68.atari.org/";
	package   = "media-sound/sc68";
	bin       = "unice68";
	args      = async r => [r.inFile(), await r.outFile("out")];
	renameOut = true;
}
