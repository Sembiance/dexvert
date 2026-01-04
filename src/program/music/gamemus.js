import {Program} from "../../Program.js";

export class gamemus extends Program
{
	website   = "https://github.com/Malvineous/libgamemusic";
	package   = "dev-libs/libgamemusic";
	flags   = {
		format : "Which format the file should be converted as"
	};
	bin       = "gamemus";
	args      = async r => [...(r.flags.format ? ["-t", r.flags.format] : []), "-l", "0", "-w", await r.outFile("out.wav"), r.inFile()];
	renameOut = true;
	chain     = "sox[type:wav]";
}
