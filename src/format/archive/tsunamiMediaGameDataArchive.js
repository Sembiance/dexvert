import {Format} from "../../Format.js";

export class tsunamiMediaGameDataArchive extends Format
{
	name           = "Tsunami Media game data archive";
	ext            = [".rlb"];
	forbidExtMatch = true;
	magic          = ["Tsunami Media game data archive"];
	converters     = ["na_game_tool_extract[format:rlb]"];
}
