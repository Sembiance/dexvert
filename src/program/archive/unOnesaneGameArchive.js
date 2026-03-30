import {Program} from "../../Program.js";
import {path} from "std";

export class unOnesaneGameArchive extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unOnesaneGameArchive"), "unOnesaneGameArchive.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
