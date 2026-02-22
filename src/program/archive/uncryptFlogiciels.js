import {Program} from "../../Program.js";

export class uncryptFlogiciels extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [Program.binPath("uncryptFlogiciels.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	chain     = "convert";
	renameOut = false;
}
