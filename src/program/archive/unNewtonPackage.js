import {Program} from "../../Program.js";
import {path} from "std";

export class unNewtonPackage extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unNewtonPackage"), "unNewtonPackage.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
