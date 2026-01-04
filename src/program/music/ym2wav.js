import {Program} from "../../Program.js";

export class ym2wav extends Program
{
	website   = "http://leonard.oxg.free.fr/stsound_download.html";
	package   = "media-sound/StSound";
	bin       = "ym2wav";
	args      = async r => [r.inFile(), await r.outFile("out.wav")];
	renameOut = true;
	chain     = "sox[type:wav]";
}
