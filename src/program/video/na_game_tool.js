import {Program} from "../../Program.js";

export class na_game_tool extends Program
{
	website = "https://nihav.org/game_tool.html";
	package = "media-video/na_game_tool";
	flags   = {
		format  : "Specify which format to treat the input file as. Run `na_game_tool --list-input-formats` for a list. Default: Let the tool decide",
		outType : `Which format to output: avi wav. Default is avi`
	};
	allowLargeOutput = true;

	bin       = "na_game_tool";
	args      = async r => [...(r.flags.format ? ["-ifmt", r.flags.format] : []), r.inFile(), "-ofmt", r.flags.outType || "avi", await r.outFile(`out.${r.flags.outType || "avi"}`)];
	chain     = r => (r.flags.outType==="wav" ? "sox" : "ffmpeg");
	renameOut = true;
}
