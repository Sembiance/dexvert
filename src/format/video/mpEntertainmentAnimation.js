import {Format} from "../../Format.js";

export class mpEntertainmentAnimation extends Format
{
	name           = "MP Entertainment Animation";
	ext            = [".anm", ".seq"];
	forbidExtMatch = true;
	magic          = ["MP Entertainment Animation"];
	converters     = ["na_game_tool"];	// let it decide between mpanim and mpanim-seq
}
