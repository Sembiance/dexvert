import {xu} from "xu";
import {Program} from "../../Program.js";

export class soundFont2tomp3 extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = Program.binPath("soundFont2tomid/soundFont2tomid.js");
	args      = r => ["--", r.inFile(), r.outDir()];
	chain     = r => `timidity[midiFont:${r.inFile({absolute : true})}]`;
	renameOut = false;
}
