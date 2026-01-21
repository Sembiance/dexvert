import {Format} from "../../Format.js";

export class conquestEarthArchive extends Format
{
	name           = "Conquest Earth WAD Archive";
	ext            = [".wad"];
	forbidExtMatch = true;
	magic          = ["Conquest Earth Archive"];
	converters     = ["na_game_tool_extract[format:ce_wad]"];
}
