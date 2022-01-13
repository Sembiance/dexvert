import {xu} from "xu";
import {Program} from "../../Program.js";

export class mencoderWinXP extends Program
{
	website      = "https://oss.netfarm.it/mplayer/";
	unsafe       = true;
	loc          = "winxp";
	checkForDups = true;
	bin          = "c:\\dexvert\\mplayer\\mencoder.exe";
	args         = r => [r.inFile(), "-o", "out.avi", "-ovc", "lavc", "-oac", "pcm"];
	qemuData     = ({
		cwd : "c:\\out"
	});
	chain        = "dexvert";
	renameOut    = true;
}
