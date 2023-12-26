import {Program} from "../../Program.js";

export class eot2ttf extends Program
{
	website   = "https://github.com/umanwizard/libeot";
	package   = "media-libs/libeot";
	bin       = "eot2ttf";
	args      = async r => [r.inFile(), await r.outFile("out.ttf")];
	renameOut = true;
	chain     = "dexvert[asFormat:font/ttf]";
}
