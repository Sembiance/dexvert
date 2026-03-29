import {Program} from "../../Program.js";
import {path} from "std";

export class unCorelThumbnails extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "python3";
	args       = r => [path.join(Program.binPath("unCorelThumbnails"), "unCorelThumbnails.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	skipVerify = true;
	renameOut  = false;
}
