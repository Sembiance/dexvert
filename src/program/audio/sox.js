import {Program} from "../../Program.js";

export class sox extends Program
{
	website = "http://sox.sourceforge.net";
	package = "media-sound/sox";
	bin     = "sox";
	args    = async r => [r.inFile(), await r.outFile("out.wav")];
	chain   = "ffmpeg[outType:mp3]";
}
