import {xu} from "xu";
import {Program} from "../../Program.js";

export class deepFreezer extends Program
{
	website   = "https://www.sac.sk/download/pack/deepf106.exe";
	loc       = "win7";
	bin       = "c:\\dexvert\\DeepF106\\DeepFreezer.exe";
	args      = r => [r.inFile()];
	unsafe    = true;
	renameOut = false;
}
