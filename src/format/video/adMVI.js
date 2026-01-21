import {Format} from "../../Format.js";

export class adMVI extends Format
{
	name           = "Archimedean Dynasty MVI Video";
	ext            = [".mvi"];
	forbidExtMatch = true;
	magic          = ["Archimedean Dynasty MVI Video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:ad_mvi]"];
}
