import {Format} from "../../Format.js";

export class eligeTuMuerteFX extends Format
{
	name           = "Elige Tu Muerte FX Video";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["Elige Tu Muerte FX WEAK"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:fx]"];
}
