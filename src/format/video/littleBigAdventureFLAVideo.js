import {xu} from "xu";
import {Format} from "../../Format.js";

export class littleBigAdventureFLAVideo extends Format
{
	name           = "Little Big Adventure FLA Video";
	ext            = [".fla"];
	forbidExtMatch = true;
	magic          = ["Little Big Adventure FLA Video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:fla]"];
}
