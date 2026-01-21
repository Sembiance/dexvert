import {Format} from "../../Format.js";

export class gteVantageAnimation extends Format
{
	name           = "GTE Vantage Animation";
	ext            = [".gav"];
	forbidExtMatch = true;
	magic          = ["GTE Vantage Animation"];
	converters     = ["na_game_tool[format:gav]"];
}
