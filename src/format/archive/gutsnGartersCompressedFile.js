import {Format} from "../../Format.js";

export class gutsnGartersCompressedFile extends Format
{
	name           = "Guts'n'Garters Compressed File";
	ext            = ["_"];
	forbidExtMatch = true;
	magic          = ["Guts'n'Garters Compressed File"];
	converters     = ["na_game_tool_extract[format:gg_]"];
}

