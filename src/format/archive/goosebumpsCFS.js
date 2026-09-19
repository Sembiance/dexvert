import {Format} from "../../Format.js";

export class goosebumpsCFS extends Format
{
	name           = "Goosebumps CFS Archive";
	ext            = [".cfs"];
	forbidExtMatch = true;
	magic          = ["Goosebumps CFS Archive", /^geArchive: CFS_FSH2( |$)/];
	converters     = ["na_game_tool_extract[format:goosebumps]", "gameextractor[codes:CFS_FSH2]"];
}
