import {Program} from "../../Program.js";
import {path} from "std";

export class vibe2glb extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	unsafe    = true;
	args      = async r => [path.join(Program.binPath("vibe2glb"), r.format.formatid, `${r.format.formatid}.py`), r.inFile({absolute : true}), await r.outFile("out.glb", {absolute : true})];
	renameOut = true;
}
