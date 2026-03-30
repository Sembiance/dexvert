import {Program} from "../../Program.js";
import {path} from "std";

export class unSetupMVA extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("setupMVA"), "unSetupMVA.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
