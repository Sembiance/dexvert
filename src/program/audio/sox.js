import {Program} from "../../Program.js";

export class sox extends Program
{
	website        = "http://sox.sourceforge.net";
	gentooPackage  = "media-sound/sox";
	gentooUseFlags = "alsa amr encode flac id3tag mad ogg openmp png sndfile twolame wavpack";
	bin            = "sox";
	args           = async r => [r.inFile(), await r.outFile("out.wav")];
	chain          = "ffmpeg[outType:mp3]";
}
