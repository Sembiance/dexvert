import {Format} from "../../Format.js";

export class goosebumpsCFS extends Format
{
	name           = "Goosebumps CFS Archive";
	ext            = [".cfs"];
	forbidExtMatch = true;
	magic          = ["Goosebumps CFS Archive"];
	converters     = ["na_game_tool_extract[format:goosebumps]"];
}
