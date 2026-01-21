import {Format} from "../../Format.js";

export class hostileWatersMNGArchive extends Format
{
	name           = "Hostile Waters MNG Archive";
	ext            = [".mng"];
	forbidExtMatch = true;
	magic          = ["Hostile Waters MNG Archive"];
	converters     = ["na_game_tool_extract[format:mng]"];
}
