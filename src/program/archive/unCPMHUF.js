import {Program} from "../../Program.js";
import {path} from "std";

export class unCPMHUF extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unCPMHUF"), "unCPMHUF.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
