import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2txt extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "python3";
	unsafe     = true;
	args       = async r => [path.join(Program.binPath("vibe2txt"), r.format.formatid, `${r.format.formatid}.py`), r.inFile({absolute : true}), await r.outFile("out.txt", {absolute : true})];
	renameOut  = true;
}
