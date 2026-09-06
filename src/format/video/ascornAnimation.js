import {Format} from "../../Format.js";

export class ascornAnimation extends Format
{
	name           = "Ascaron animation";
	ext            = [".anm"];
	forbidExtMatch = true;
	magic          = ["Ascaron animation"];
	converters     = ["na_game_tool[format:asc_anim]"];
}
