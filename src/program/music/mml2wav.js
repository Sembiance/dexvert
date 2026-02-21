import {Program} from "../../Program.js";
import {path} from "std";

export class mml2wav extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = async r => [path.join(Program.binPath("mml2wav"), "mml2wav.py"), r.inFile({absolute : true}), await r.outFile("out.wav", {absolute : true})];
	renameOut = true;
	chain     = "sox[type:wav]";
}
