import {Program} from "../../Program.js";

export class undiskcopy extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [Program.binPath("undiskcopy.py"), r.inFile({absolute : true}), await r.outFile("out.img", {absolute : true})];
	renameOut = true;
}
