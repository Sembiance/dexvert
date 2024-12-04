import {xu} from "xu";
import {Format} from "../../Format.js";

export class legendEntertainmentQ extends Format
{
	name           = "Legend Entertainment Q Video";
	website        = "https://wiki.multimedia.cx/index.php/Legend_Entertainment_Q";
	ext            = [".q"];
	forbidExtMatch = true;
	magic          = ["Mission Critical video/animation"];
	converters     = ["na_game_tool[format:q]"];
}
