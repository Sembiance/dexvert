import {Program} from "../../Program.js";

export class optimFROG extends Program
{
	website   = "http://losslessaudio.org/";
	loc       = "wine";
	bin       = "OptimFROG_Win_x86_5100\\ofr.exe";
	args      = async r => ["--decode", r.inFile(), "--output", await r.outFile("out.wav")];
	renameOut = true;
	chain     = "sox";
}
