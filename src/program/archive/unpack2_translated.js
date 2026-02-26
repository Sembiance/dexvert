import {Program} from "../../Program.js";

export class unpack2_translated extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = Program.binPath("unpack2_translated");
	args      = r => [r.inFile({absolute : true})];
	cwd       = r => r.outDir();
	renameOut = false;
}
