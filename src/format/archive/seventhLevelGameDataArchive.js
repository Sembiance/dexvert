import {Format} from "../../Format.js";

export class seventhLevelGameDataArchive extends Format
{
	name           = "7th Level Game Data Archive";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = ["7th Level Archive", "7th Level game data archive"];
	converters     = ["na_game_tool_extract[format:7lev_bin]"];
}
