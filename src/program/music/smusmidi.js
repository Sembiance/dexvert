import {Program} from "../../Program.js";

export class smusmidi extends Program
{
	website   = "https://aminet.net/package/mus/midi/SMUSMIDI.lha";
	unsafe    = true;
	bin       = "vamos";
	args      = async r => [...Program.vamosArgs("SMUSMIDI"), r.inFile(), await r.outFile("out")];
	renameOut = true;
	chain     = "timidity";
}
