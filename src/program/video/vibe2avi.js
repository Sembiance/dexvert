import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2avi extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [path.join(Program.binPath("vibe2avi"), r.format.formatid, `${r.format.formatid}.py`), r.inFile(), await r.outFile("out.avi")];
	renameOut = true;
	chain      = "ffmpeg";
}
