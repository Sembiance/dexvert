import {Program} from "../../Program.js";

export class gd2topng extends Program
{
	website   = "https://libgd.org";
	package   = "media-libs/gd";
	bin       = "gd2topng";
	args      = async r => [r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
