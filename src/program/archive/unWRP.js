import {Program} from "../../Program.js";
import {path} from "std";

export class unWRP extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("wrp"), "unWRP.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
