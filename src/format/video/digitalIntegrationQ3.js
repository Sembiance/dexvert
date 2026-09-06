import {Format} from "../../Format.js";

export class digitalIntegrationQ3 extends Format
{
	name           = "Digital Integration Q3";
	ext            = [".q3"];
	forbidExtMatch = true;
	magic          = ["Digital Integration Q3"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:q3]"];
}
