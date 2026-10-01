import {Format} from "../../Format.js";

export class hostileWatersMNGArchive extends Format
{
	name           = "Hostile Waters MNG Archive";
	ext            = [".mng"];
	forbidExtMatch = true;
	magic          = ["Hostile Waters MNG Archive", /^geArchive: MNG_ZGWH( |$)/];
	converters     = ["na_game_tool_extract[format:mng]", "gameextractor[codes:MNG_ZGWH]"];
}
