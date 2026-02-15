import {Program} from "../../Program.js";
import {path} from "std";

export class ilbm2apng extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	unsafe    = true;
	args      = async r => [path.join(Program.binPath("ilbm2apng"), "ilbm2apng.py"), r.inFile({absolute : true}), await r.outFile("out.png", {absolute : true})];
	renameOut = true;
}
