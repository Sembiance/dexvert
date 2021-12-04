import {Program} from "../../Program.js";

export class vgmstream extends Program
{
	website       = "https://github.com/vgmstream/vgmstream";
	gentooPackage = "media-sound/vgmstream-cli";
	gentooOverlay = "dexvert";
	bin           = "vgmstream-cli";
	args          = async r => ["-o", await r.outFile("out.wav"), "-i", r.inFile()];
	chain         = "ffmpeg[outType:mp3]";
}
