import {Format} from "../../Format.js";

export class southPeakPuzzleArchive extends Format
{
	name           = "SouthPeak Puzzle Archive";
	ext            = [".mco"];
	forbidExtMatch = true;
	magic          = ["SouthPeak Puzzle Archive"];
	converters     = ["na_game_tool_extract[format:mco]"];
}
