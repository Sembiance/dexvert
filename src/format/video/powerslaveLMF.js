import {Format} from "../../Format.js";

export class powerslaveLMF extends Format
{
	name           = "Powerslave LMF Video";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["Powerslave LMF"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:lmf]"];
}
