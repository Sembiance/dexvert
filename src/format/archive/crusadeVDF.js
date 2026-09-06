import {Format} from "../../Format.js";

export class crusadeVDF extends Format
{
	name           = "Crusade VDF Archive";
	ext            = [".vdf"];
	forbidExtMatch = true;
	magic          = ["Crusade VDF"];
	converters     = ["na_game_tool_extract[format:vdf]"];
}
