import {Format} from "../../Format.js";

export class ascornEntertainmentAnimation extends Format
{
	name           = "ASCARON Entertainment Animation";
	ext            = [".anm"];
	forbidExtMatch = true;
	magic          = ["ASCARON Entertainment Animation"];
	converters     = ["na_game_tool[format:ascon]"];
}
