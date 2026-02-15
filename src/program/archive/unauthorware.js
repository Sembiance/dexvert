import {Program} from "../../Program.js";
import {path} from "std";

export class unauthorware extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("unauthorware"), "unauthorware.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	cwd       = r => r.outDir();
	renameOut = false;
	notes     = "Extractor vibe coded with claude code";
}
