import {xu} from "xu";
import {Program} from "../../Program.js";

export class adplay extends Program
{
	website    = "https://github.com/adplug/adplay-unix";
	package    = "media-sound/adplay";
	bin        = "adplay";
	args       = async r => ["-O", "disk", "-d", await r.outFile("out.wav"), r.inFile()];
	runOptions = ({timeout : xu.MINUTE*2});

	// adplay often fails to produce a valid wav but does produce a 44 byte wav file of nothing
	verify    = (r, dexFile) => dexFile.size!==44;
	renameOut = true;
	chain     = "sox";
}
