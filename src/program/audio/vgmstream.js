import {Program} from "../../Program.js";

export class vgmstream extends Program
{
	website   = "https://github.com/vgmstream/vgmstream";
	package   = "media-sound/vgmstream-cli";
	bin       = "vgmstream-cli";
	args      = async r => ["-o", await r.outFile("out.wav"), "-i", r.inFile()];
	chain     = "sox";
	renameOut = true;
}
