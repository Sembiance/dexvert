import {Format} from "../../Format.js";

export class eclipseVoiceArchive extends Format
{
	name           = "Eclipse Voice Archive";
	ext            = [".fvt"];
	forbidExtMatch = true;
	magic          = ["Eclipse Voice Archive"];
	converters     = ["na_game_tool_extract[format:fvt]"];
}

