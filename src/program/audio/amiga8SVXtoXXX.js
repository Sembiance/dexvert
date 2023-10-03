import {Program} from "../../Program.js";

export class amiga8SVXtoXXX extends Program
{
	website   = "https://aminet.net/package/mus/misc/8SVXtoXXX";
	unsafe    = true;
	bin       = "8SVXtoXXX";
	args      = r => [...Program.vamosArgs("8SVXtoXXX"), "INPUT", r.inFile(), "OUTPUT", "system:out.wav"];
	chain     = "sox";
	renameOut = true;
}
