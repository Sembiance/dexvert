import {Program} from "../../Program.js";

export class pack extends Program
{
	website   = "https://liballeg.org/";
	package   = "media-libs/allegro";
	bin       = "pack";
	args      = async r => ["u", r.inFile(), await r.outFile("out")];
	renameOut = true;
}
