import {Program} from "../../Program.js";

export class xmp extends Program
{
	website        = "http://xmp.sourceforge.net/";
	gentooPackage  = "media-sound/xmp";
	gentooOverlay  = "dexvert";
	gentooUseFlags = "alsa";
	bin            = "xmp";
	args           = async r => ["--quiet", "-o", await r.outFile("out.wav"), r.inFile()];
	
	// xmp often fails to produce a valid wav but does produce a 44 byte wav file of nothing, so if it's a 44 byte file it should fail validation
	verify = (r, dexFile) => dexFile.size!==44;
	chain  = "ffmpeg[outType:mp3]";
}
