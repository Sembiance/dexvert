import {xu} from "xu";
import {Program} from "../../Program.js";

export class mencoderWinXP extends Program
{
	website      = "https://oss.netfarm.it/mplayer/";
	flags   = {
		outType     : `Which format to output: avi mp3. Default is avi`
	};
	unsafe       = true;
	loc          = "winxp";
	checkForDups = true;
	bin          = "c:\\dexvert\\mplayer\\mencoder.exe";
	args         = r => [r.inFile(), "-o", `out.${r.flags.outType || "avi"}`, "-ovc", "lavc", "-oac", "pcm"];
	qemuData     = ({
		cwd : "c:\\out"
	});
	chain        = "dexvert";
	renameOut    = true;
}
