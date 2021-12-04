import {Program} from "../../Program.js";

export class amiga8SVXtoXXX extends Program
{
	website = "https://aminet.net/package/mus/misc/8SVXtoXXX";
	unsafe  = true;
	loc     = "amigappc";
	bin     = "8SVXtoXXX";
	args    = r => ["INPUT", r.inFile(), "OUTPUT", "HD:out/out.wav"];
	chain   = "ffmpeg[outType:mp3]";
}
