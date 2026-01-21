import {Format} from "../../Format.js";

export class escalCompressed extends Format
{
	name       = "Escal Compressed File";
	magic      = ["Escal Compressed"];
	converters = ["na_game_tool_extract[format:escal-z]"];
}
