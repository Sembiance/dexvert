import {Format} from "../../Format.js";

export class knowledgeAdventureDataArchive extends Format
{
	name           = "Knowledge Adventure Data Archive";
	ext            = [".iml", ".rld"];
	forbidExtMatch = true;
	magic          = ["Knowledge Adventure Archive", "Knowledge Adventure data archive"];
	converters     = ["na_game_tool_extract[format:kaa-new]"];
}
