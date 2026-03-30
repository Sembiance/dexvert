import {Program} from "../../Program.js";
import {path} from "std";

export class unStuffitX extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("stuffitX"), "unStuffitX.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = false;
}
