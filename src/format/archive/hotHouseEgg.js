import {Format} from "../../Format.js";

export class hotHouseEgg extends Format
{
	name           = "Hot House EGG Archive";
	ext            = [".egg"];
	forbidExtMatch = true;
	magic          = ["EGG video"];	// also valid for actual video files, but only from the game Independence Day, which doesn't appear anywhere on discmaster
	converters     = ["na_game_tool_extract[format:egg]"];
}
