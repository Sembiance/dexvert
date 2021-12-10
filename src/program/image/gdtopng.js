import {Program} from "../../Program.js";

export class gdtopng extends Program
{
	website   = "https://libgd.org";
	package   = "media-libs/gd";
	unsafe    = true;
	bin       = "gdtopng";
	args      = async r => [r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
