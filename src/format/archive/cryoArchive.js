import {Format} from "../../Format.js";

export class cryoArchive extends Format
{
	name           = "Cryo Archive";
	ext            = [".big", ".hnm"];
	forbidExtMatch = true;
	magic          = ["Cryo Archive", "CRYO HNM4 video"];
	converters     = ["na_game_tool_extract[format:cryo_archive]"];
}
