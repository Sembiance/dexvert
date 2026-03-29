import {Program} from "../../Program.js";
import {path} from "std";

export class unAmigaPFS extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unAmigaPFS"), "unAmigaPFS.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
