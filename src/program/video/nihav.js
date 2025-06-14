import {xu} from "xu";
import {Program} from "../../Program.js";

export class nihav extends Program
{
	website = "https://git.nihav.org/";
	package = "media-video/nihav";
	flags   = {
		outType : `Which format to output: avi mp3. Default is avi`
	};
	bin        = "nihav-encoder";
	args       = async r => ["--input", r.inFile(), "--output", await r.outFile(`out.avi`), "--profile", "lossless"];
	runOptions = {timeout : xu.MINUTE*10};
	chain      = r => (r.flags.outType==="mp3" ? "ffmpeg[outType:mp3]" : "ffmpeg");
	renameOut  = true;
}
