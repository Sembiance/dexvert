import {Program} from "../../Program.js";

export class mikmod2wav extends Program
{
	website = "https://github.com/Sembiance/mikmod2wav";
	package = "media-sound/mikmod2wav";
	unsafe  = true;
	bin     = "mikmod2wav";
	args    = async r => ["--limitSeconds", "900", r.inFile(), await r.outFile("out.wav")];
	chain   = "ffmpeg[outType:mp3]";
}
