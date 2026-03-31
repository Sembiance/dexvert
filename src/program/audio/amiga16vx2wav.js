import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class amiga16vx2wav extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [path.join(Program.binPath("amiga16vx"), "amiga16vx2wav.py"), r.inFile(), await r.outFile("out.wav")];
	renameOut = true;
	chain     = "sox[type:wav]";
}
