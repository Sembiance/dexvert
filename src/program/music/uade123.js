import {Program} from "../../Program.js";

export class uade123 extends Program
{
	website = "http://zakalwe.fi/uade";
	package = "app-emulation/uade";
	flags   = {
		player      : "Which 'player' file to use for conversion. Find a list in `ls /usr/share/uade/players/` Default: Let uade123 decide",
		maxDuration : "Maximum duration (in seconds) to allow the output file to be. Default: 10 minutes"
	};
	bin  = "uade123";
	args = async r => [...(r.flags.player ? ["-P", `/usr/share/uade/players/${r.flags.player}`] : []), "-t", r.flags.maxDuration || 600, "-e", "wav", "-f", await r.outFile("out.wav"), r.inFile()];

	// uade often fails to produce a valid wav but does produce a 68 byte wav file of nothing
	verify    = (r, dexFile) => dexFile.size!==68;
	renameOut = true;
	chain     = "sox[type:wav]";
}
