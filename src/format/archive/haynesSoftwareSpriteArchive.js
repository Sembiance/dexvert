import {Format} from "../../Format.js";

export class haynesSoftwareSpriteArchive extends Format
{
	name           = "Haynes Software Sprite Archive";
	ext            = [".spp"];
	forbidExtMatch = true;
	magic          = ["Haynes Software Sprite Archive"];
	converters     = ["na_game_tool_extract[format:spp]"];
}
