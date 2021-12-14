import {Program} from "../../Program.js";

export class seq2mp4 extends Program
{
	website   = "https://github.com/Sembiance/seq2mp4";
	package   = "media-gfx/seq2mp4";
	unsafe    = true;
	bin       = "seq2mp4";
	args      = async r => [r.inFile(), await r.outFile("out.mp4")];
	renameOut = true;
	chain     = "ffmpeg";	// to fix encoding so it works with websites better
}
