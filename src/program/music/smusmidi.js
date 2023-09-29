import {Program} from "../../Program.js";

export class smusmidi extends Program
{
	website   = "https://aminet.net/package/mus/midi/SMUSMIDI.lha";
	unsafe    = true;
	loc       = "amiga";
	bin       = "SMUSMIDI";
	args      = r => [r.inFile(), "HD:out/out"];
	renameOut = true;
	chain     = "timidity";
}
