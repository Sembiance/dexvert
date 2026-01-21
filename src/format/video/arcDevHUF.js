import {Format} from "../../Format.js";

export class arcDevHUF extends Format
{
	name           = "Arc Developments HUF Video";
	ext            = [".huf"];
	forbidExtMatch = true;
	magic          = ["Arc Developments HUF Video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:arc-huf]"];
}
