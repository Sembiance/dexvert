import {Program} from "../../Program.js";

export class na_game_tool_extract extends Program
{
	website = "https://nihav.org/game_tool.html";
	package = "media-video/na_game_tool";
	flags   = {
		format  : "Specify which format to treat the input file as. Run `na_game_tool --list-archive-formats` for a list"
	};
	bin       = "na_game_tool";
	args      = r => ["-extract", ...(r.flags.format ? ["-ifmt", r.flags.format] : []), r.inFile(), r.outDir()];
	renameOut = false;
}
