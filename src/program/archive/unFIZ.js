import {Program} from "../../Program.js";
import {path} from "std";

export class unFIZ extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unFIZ"), "unFIZ.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
