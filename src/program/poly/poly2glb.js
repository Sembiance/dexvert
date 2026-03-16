import {Program} from "../../Program.js";
import {path} from "std";

export class poly2glb extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	bin     = "python3";
	flags   = {
		type : `Input file type. Required.`
	};
	args      = async r => [path.join(Program.binPath("poly2glb"), "poly2glb.py"), r.flags.type, r.inFile({absolute : true}), await r.outFile("out.glb", {absolute : true})];
	renameOut = true;
}
