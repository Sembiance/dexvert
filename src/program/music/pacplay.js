import {Program} from "../../Program.js";

export class pacplay extends Program
{
	website   = "https://libpac.sourceforge.net/";
	package   = "media-libs/libpac";
	bin       = "pacplay";
	args      = async r => [r.inFile(), await r.outFile("out.wav")];
	renameOut = true;
	chain     = "sox";
}
