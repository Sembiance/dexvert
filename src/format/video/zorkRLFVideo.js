import {Format} from "../../Format.js";

export class zorkRLFVideo extends Format
{
	name           = "Zork RLF video";
	website        = "https://wiki.multimedia.cx/index.php/RLF";
	ext            = [".rlf"];
	forbidExtMatch = true;
	magic          = ["Zork RLF video"];
	converters     = ["na_game_tool[format:rlf]"];
}
