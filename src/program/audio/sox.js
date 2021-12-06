import {Program} from "../../Program.js";

export class sox extends Program
{
	website     = "http://sox.sourceforge.net";
	package     = "media-sound/sox";
	bin         = "sox";
	args        = async r => [r.inFile(), await r.outFile("out.wav")];
	
	// We often send WAV files through SOX just to clean them up before going to FFMPEG. This sometimes results in an identical output file which is normally detected and deleted, but in this case we want to allow it
	allowDupOut = true;
	
	chain = "ffmpeg[outType:mp3]";
}
