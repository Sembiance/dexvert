import {Program} from "../../Program.js";
import {path} from "std";

export class unAIXBFF extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unAIXBFF"), "unAIXBFF.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
