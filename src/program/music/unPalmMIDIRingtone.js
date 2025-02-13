import {xu} from "xu";
import {Program} from "../../Program.js";

export class unPalmMIDIRingtone extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("unPalmMIDIRingtone.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	chain      = "timidity";
	renameOut  = false;
}
