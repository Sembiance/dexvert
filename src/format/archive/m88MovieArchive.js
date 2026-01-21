import {Format} from "../../Format.js";

export class m88MovieArchive extends Format
{
	name           = "M88 Movie Archive";
	ext            = [".m88"];
	forbidExtMatch = true;
	magic          = ["M88 Movie Archive"];
	converters     = ["na_game_tool_extract[format:m88]"];
}
